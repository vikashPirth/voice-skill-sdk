#
# voice-skill-sdk
#
# (C) 2020, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import unittest
from unittest.mock import patch
from requests.sessions import Session
from skill_sdk.tracing import (
    global_tracer,
    initialize_tracer,
    set_global_tracer,
    start_span,
    start_active_span,
    Codec,
    Format,
    InvalidCarrierException,
    SpanContext,
    UnsupportedFormatException,
)


class TestTracing(unittest.TestCase):

    def setUp(self):
        initialize_tracer()

    def test_start_span(self):
        with self.assertRaises(ValueError):
            set_global_tracer(None)

        with start_span('test_span') as span:
            self.assertIsNotNone(span.tracer)
            self.assertEqual(span.operation_name, 'test_span')
            with start_span('another_one', child_of=span) as child_span:
                self.assertEqual(child_span.operation_name, 'another_one')
                self.assertEqual(child_span.context.trace_id, span.context.trace_id)

    @patch('skill_sdk.tracing.Tracer.start_span')
    def test_start_span_decorator(self, start_mock):
        @start_span('test_span')
        def decorated_func():
            return True

        decorated_func()
        start_mock.assert_called_once_with('test_span')


class TestNoopCodec(unittest.TestCase):

    def setUp(self):
        initialize_tracer()

    def test_extract(self):
        codec = Codec()

        with self.assertRaises(InvalidCarrierException):
            codec.extract([])

        # Implicit case insensitivity testing
        carrier = {'X-b3-SpanId': 'a2fb4a1d1a96d312',
                   'X-B3-traceId': '463ac35c9f6413ad48485a3953bb6124',
                   'baggage-x-magenta-transaction-id': '42',
                   'X-tenant-id': 'tenant-id',
                   'X-Testing': '1'}

        span_context = codec.extract(carrier)
        assert span_context.span_id == 'a2fb4a1d1a96d312'
        assert span_context.trace_id == '463ac35c9f6413ad48485a3953bb6124'
        assert span_context.baggage == {'testing': True, 'transaction_id': '42', 'tenant_id': 'tenant-id'}

    def test_b3_inject(self):
        codec = Codec()

        with self.assertRaises(InvalidCarrierException):
            codec.inject(None, [])

        ctx = SpanContext(trace_id='463ac35c9f6413ad48485a3953bb6124',
                          span_id='a2fb4a1d1a96d312',
                          baggage={
                              'testing': '1',
                              'transaction_id': '42',
                              'tenant_id': 'tenant'}
                          )
        carrier = {}
        codec.inject(ctx, carrier)
        self.assertEqual({
            'X-B3-SpanId': 'a2fb4a1d1a96d312',
            'X-B3-TraceId': '463ac35c9f6413ad48485a3953bb6124',
            'X-Testing': '1',
            'Testing': 'true',
            'Baggage-X-Magenta-Transaction-Id': '42',
            'X-Tenant-Id': 'tenant',
        }, carrier)

    def test_extract_inject_exceptions(self):
        tracer = global_tracer()
        with self.assertRaises(UnsupportedFormatException):
            tracer.extract('Unknown', {})
        ctx = SpanContext(None, None, None)
        with self.assertRaises(UnsupportedFormatException):
            tracer.inject(ctx, 'Unknown', {})

    @patch.object(Session, 'request')
    def test_baggage_propagation(self, req_mock):
        tracer = initialize_tracer()
        with patch('skill_sdk.tracing.global_tracer', return_value=tracer):
            request = unittest.mock.Mock()
            request.headers = {
                "X-B3-SpanId": "a2fb4a1d1a96d312",
                "X-B3-TraceId": "463ac35c9f6413ad48485a3953bb6124",
                "X-Testing": "1",
                "Baggage-X-Magenta-Transaction-Id": "42",
                "X-Tenant-Id": "tenant",
            }
            with start_active_span('span', request) as scope:
                assert scope.span.context.baggage["transaction_id"] == '42'

                from skill_sdk.requests import CircuitBreakerSession
                with CircuitBreakerSession(internal=True) as session:
                    session.get("http://localhost")
                    self.assertEqual(req_mock.call_args_list[0][1].get("headers"), {
                        **request.headers,
                        **{"Testing": "true", "X-B3-SpanId": "2"}
                    })
