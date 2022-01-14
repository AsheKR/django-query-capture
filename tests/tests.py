from unittest.mock import Mock

from django.test import TestCase
from news.models import Reporter

from django_query_capture import query_capture


class QueryCaptureTests(TestCase):
    def setUp(self) -> None:
        Reporter.objects.create(full_name="target")

    def test_capture_query_in_context_manager(self):
        with query_capture() as q:
            Reporter.objects.create(full_name="target-1")
            Reporter.objects.create(full_name="target-2")
            self.assertEqual(len(q), 2)

    # TODO: Change to a test to see if the query is captured when using Decorator.
    def test_capture_query_in_decorator(self):
        func = Mock()
        query_capture()(func)()
        self.assertTrue(func.called)
