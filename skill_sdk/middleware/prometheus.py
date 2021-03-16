#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

#
# Prometheus middleware
#

import time
import logging
from functools import wraps
from typing import Any, Callable, Text
from contextlib import contextmanager, ContextDecorator
from fastapi import FastAPI

from skill_sdk.config import settings

logger = logging.getLogger(__name__)

HTTP_REQUESTS_LATENCY_SECONDS = "http_requests_latency_seconds"
HTTP_PARTNER_REQUEST_COUNT = "http_partner_request_count"

try:
    from starlette_exporter import PrometheusMiddleware, handle_metrics
    from prometheus_client import Counter, Histogram
except ModuleNotFoundError:
    logger.error(
        '"PrometheusMiddleware" not found. Extra package is not installed. '
        'Make sure to install "skill-sdk[all]" to export Prometheus metrics.'
    )
    raise


class Prometheus(PrometheusMiddleware):
    @staticmethod
    def requests_latency():
        metric_name = HTTP_REQUESTS_LATENCY_SECONDS
        if metric_name not in PrometheusMiddleware._metrics:
            PrometheusMiddleware._metrics[metric_name] = Histogram(
                metric_name,
                "HTTP Requests Latency in second",
                ("job", "version", "operation"),
            )
        return PrometheusMiddleware._metrics[metric_name]

    @staticmethod
    def partner_requests_count():
        metric_name = HTTP_PARTNER_REQUEST_COUNT
        if metric_name not in PrometheusMiddleware._metrics:
            PrometheusMiddleware._metrics[metric_name] = Counter(
                metric_name,
                "HTTP Requests for services",
                ("job", "partner_name", "status"),
            )
        return PrometheusMiddleware._metrics[metric_name]


class prometheus_latency(ContextDecorator):  # noqa
    """
    Prometheus latency wrapper. Can be used as context manager and decorator:

        # As context manager:
        with prometheus_latency("operation_name"):
            ...

        # As decorator:
        @prometheus_latency("operation_name")
        def decorated():
            ...

    """

    def __init__(self, operation_name: Text):
        self.operation_name = operation_name

    def __enter__(self):
        self.begin = time.perf_counter()

    def __exit__(self, exc_type, exc, exc_tb):
        end = time.perf_counter()

        labels = [settings.SKILL_NAME, settings.SKILL_VERSION, self.operation_name]
        Prometheus.requests_latency().labels(*labels).observe(end - self.begin)


@contextmanager
def partner_call(partner_name: Text, func: Callable[..., Any]):
    """
    Context manager to count HTTP requests to partner services

        ...
        with partner_call('partner-service-name', client.get) as get:
            response = get(URL)

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)

        try:
            status_code = response.status_code
            labels = [settings.SKILL_NAME, partner_name, status_code]
            Prometheus.partner_requests_count().labels(*labels).inc()
        except AttributeError as ex:
            logger.error("Cannot log a partner call: %s", repr(ex))

        return response

    yield wrapper


def setup(app: FastAPI) -> None:

    app.add_middleware(
        Prometheus,
        app_name=settings.SKILL_NAME,
        prefix="http",
    )

    route = getattr(settings, "PROMETHEUS_ENDPOINT", "/prometheus")
    app.add_route(route, handle_metrics)
