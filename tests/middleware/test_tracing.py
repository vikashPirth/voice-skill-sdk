#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import time
from unittest.mock import patch

import jaeger_client.reporter
import opentracing.scope_managers.asyncio
from fastapi.testclient import TestClient
from skill_sdk import init_app, skill, util
from skill_sdk.middleware import tracing


@patch("opentracing.Span.__enter__")
@patch("opentracing.Span.__exit__")
def test_start_span(exit_mock, enter_mock):
    with tracing.start_span("test_span") as span:
        assert span.operation_name == "test_span"
        enter_mock.assert_called_once()
    exit_mock.assert_called_once()


@patch("opentracing.Span.__enter__")
@patch("opentracing.Span.__exit__")
def test_start_span_decorator(exit_mock, enter_mock):
    @tracing.start_span("test_span")
    def decorated_func():
        enter_mock.assert_called_once()
        exit_mock.assert_not_called()

    decorated_func()

    exit_mock.assert_called_once()


def test_with_jaeger_client():
    from jaeger_client import Config
    from opentracing.scope_managers.contextvars import ContextVarsScopeManager

    config = Config(
        config={
            "sampler": {"type": "const", "param": 1},
            "propagation": "b3",
            "logging": False,
        },
        scope_manager=ContextVarsScopeManager(),
        service_name="my-app",
    )

    tracer = config.initialize_tracer()
    app = init_app(develop=True)
    tracing.setup(app, tracer)

    @app.intent_handler("Trace_Intent")
    def handle():
        with tracing.start_span("sub-span"):
            return "Hola"

    client = TestClient(app)
    with patch.object(jaeger_client.reporter.Reporter, "report_span") as reporter_mock:
        client.post(
            "/v1/skill-noname",
            json=util.create_request("Trace_Intent").dict(),
            headers={
                'X-B3-TraceId': '430ee1c3e2deccfa',
                'X-B3-SpanId': 'd4aeec01e3c43faa',
                'X-B3-Sampled': '1',
            },
        )

        # Ensure 2 spans with trace_id="430ee1c3e2deccfa" are reported,
        # and the second is a child span of the first
        assert len(reporter_mock.call_args_list) == 2
        span = reporter_mock.call_args_list[1][0][0]
        sub_span = reporter_mock.call_args_list[0][0][0]
        assert '{:x}'.format(span.trace_id) == '{:x}'.format(sub_span.trace_id) == "430ee1c3e2deccfa"
        assert span.span_id == sub_span.parent_id
