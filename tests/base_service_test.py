import unittest
from skill_sdk import tracing

tracing.initialize_tracer()


class TestBaseService(unittest.TestCase):

    def test_no_base_url(self):
        from skill_sdk.services.base import BaseService
        b = BaseService()
        with self.assertRaises(ValueError):
            self.assertEqual(b.url, None)
