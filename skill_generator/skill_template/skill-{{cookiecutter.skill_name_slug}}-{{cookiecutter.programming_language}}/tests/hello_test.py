import unittest

from impl.hello import skill


class TestMain(unittest.TestCase):

    def test_hello_handler(self):
        """ A simple test case to ensure that our implementation returns 'Hello'
        """
        response = skill.test_intent('SMALLTALK__GREETINGS')
        self.assertEqual(response.text.key, 'HELLOAPP_HELLO')
