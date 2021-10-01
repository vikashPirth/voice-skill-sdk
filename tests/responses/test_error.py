#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#
#

from skill_sdk.responses import (
    ErrorCode,
    ErrorResponse,
)


def test_init():
    er = ErrorResponse(code=999, text="internal error")
    assert er.code == 999
    assert er.text == "internal error"


def test_as_response_400():
    er = ErrorResponse(code=ErrorCode.INVALID_TOKEN, text="invalid token")
    assert er.code == 2
    assert er.text == "invalid token"


def test_as_response_500():
    er = ErrorResponse(code=ErrorCode.INTERNAL_ERROR, text="unhandled exception")
    assert er.code == 999
    assert er.text == "unhandled exception"
