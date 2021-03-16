#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

import unittest
from unittest.mock import patch


class TestTracing(unittest.TestCase):
    @patch("opentracing.Span.__enter__")
    @patch("opentracing.Span.__exit__")
    def test_start_span(self, exit_mock, enter_mock):
        from skill_sdk.middleware.tracing import start_span

        with start_span("test_span") as span:
            self.assertEqual(span.operation_name, "test_span")
            enter_mock.assert_called_once()
        exit_mock.assert_called_once()

    @patch("opentracing.Span.__enter__")
    @patch("opentracing.Span.__exit__")
    def test_start_span_decorator(self, exit_mock, enter_mock):
        from skill_sdk.middleware.tracing import start_span

        @start_span("test_span")
        def decorated_func():
            enter_mock.assert_called_once()
            exit_mock.assert_not_called()

        decorated_func()

        exit_mock.assert_called_once()
