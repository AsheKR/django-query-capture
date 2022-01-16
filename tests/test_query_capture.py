from django.test import TestCase, override_settings
from news.models import Reporter

from django_query_capture import query_capture


class QueryCaptureTestCases(TestCase):
    def test_something(self):
        with query_capture() as capture:
            Reporter.objects.create(full_name=f"target-1")
            self.assertEqual(len(capture.captured_queries), 1)
            Reporter.objects.create(full_name=f"target-2")
            self.assertEqual(len(capture.captured_queries), 2)
