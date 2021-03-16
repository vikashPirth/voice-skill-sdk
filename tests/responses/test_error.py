#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

import unittest

from skill_sdk.responses import (
    ErrorCode,
    ErrorResponse,
)


class TestErrorResponse(unittest.TestCase):
    def test_init(self):
        er = ErrorResponse(code=999, text="internal error")
        self.assertEqual(er.code, 999)
        self.assertEqual(er.text, "internal error")

    def test_as_response_400(self):
        er = ErrorResponse(code=ErrorCode.INVALID_TOKEN, text="invalid token")
        self.assertEqual(er.code, 2)
        self.assertEqual(er.text, "invalid token")

    def test_as_response_500(self):
        er = ErrorResponse(code=ErrorCode.INTERNAL_ERROR, text="unhandled exception")
        self.assertEqual(er.code, 999)
        self.assertEqual(er.text, "unhandled exception")
