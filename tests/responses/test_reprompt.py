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
from unittest.mock import patch

from skill_sdk.responses import Response, Reprompt

from skill_sdk.util import create_context


class TestReprompt(unittest.TestCase):
    def setUp(self):
        self.ctx = create_context("TELEKOM_Clock_GetTime")


"""
    def test_reprompt_response(self):
        self.assertIsInstance(Reprompt('abc123'), Response)
        response = Reprompt('abc123').dict(self.ctx)
        self.assertEqual(response['session']['attributes']['TELEKOM_Clock_GetTime_reprompt_count'], '1')
        self.assertEqual(response['text'], 'abc123')
        self.assertEqual(response['type'], 'ASK')
        with patch.dict(self.ctx.session, {'TELEKOM_Clock_GetTime_reprompt_count': '1'}):
            response = Reprompt('abc123').dict(self.ctx)
            self.assertEqual(response['session']['attributes']['TELEKOM_Clock_GetTime_reprompt_count'], '2')
            self.assertEqual(response['text'], 'abc123')
            self.assertEqual(response['type'], 'ASK')
            response = Reprompt('abc123', '321cba', 2).dict(self.ctx)
            self.assertNotIn('TELEKOM_Clock_GetTime_reprompt_count', response['session']['attributes'])
            self.assertEqual(response['text'], '321cba')
            self.assertEqual(response['type'], 'TELL')
        with patch.dict(self.ctx.session, {'TELEKOM_Clock_GetTime_reprompt_count': 'not a number'}):
            response = Reprompt('abc123').dict(self.ctx)
            self.assertEqual(response['session']['attributes']['TELEKOM_Clock_GetTime_reprompt_count'], '1')
        response = Reprompt('abc123', entity='Time').dict(self.ctx)
        self.assertEqual(response['session']['attributes']['TELEKOM_Clock_GetTime_reprompt_count'], '1')
        self.assertEqual(response['session']['attributes']['TELEKOM_Clock_GetTime_Time_reprompt_count'], '1')
"""
