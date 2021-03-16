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
# Logging middleware: extract headers for logging
#

from enum import Enum
from starlette_context.plugins.base import Plugin


class HeaderKeys(str, Enum):
    trace_id = "X-B3-TraceId"
    span_id = "X-B3-SpanId"
    tenant_id = "X-TenantId"
    testing_flag = "X-Testing"


class TraceIdPlugin(Plugin):
    key = HeaderKeys.trace_id


class SpanIdIdPlugin(Plugin):
    key = HeaderKeys.span_id


class TenantIdIdPlugin(Plugin):
    key = HeaderKeys.tenant_id


class TestingFlagPlugin(Plugin):
    key = HeaderKeys.testing_flag
