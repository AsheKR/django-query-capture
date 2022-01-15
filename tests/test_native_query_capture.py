from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone
from news.models import Article, Reporter

from django_query_capture import native_query_capture


class NativeQueryCaptureTests(TestCase):
    def setUp(self) -> None:
        Reporter.objects.create(full_name="target")

    def test_capture_query_in_context_manager(self):
        with native_query_capture() as q:
            r = Reporter.objects.create(full_name="target-1")
            Article.objects.create(
                pub_date=timezone.now().date(),
                headline="headline",
                content="content",
                reporter=r,
            )
            self.assertEqual(len(q), 2)

    # TODO: Change to a test to see if the query is captured when using Decorator.
    def test_capture_query_in_decorator(self):
        func = Mock()
        native_query_capture()(func)()
        self.assertTrue(func.called)
