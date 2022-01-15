from unittest.mock import Mock

from django.test import TestCase, modify_settings
from news.models import Reporter
from test_presenter.utils import ConsoleOutputTestCaseMixin

from django_query_capture import QueryCaptureMiddleware


def get_response(request):
    [Reporter.objects.create(full_name=f"target-{i}") for i in range(12)]
    [list(Reporter.objects.all()) for i in range(11)]


@modify_settings(
    MIDDLEWARE={
        "append": "django_query_capture.middleware.QueryCaptureMiddleware",
    }
)
class QueryCaptureMiddlewareTests(ConsoleOutputTestCaseMixin, TestCase):
    def test_query_capture_duplicate(self):
        middleware = QueryCaptureMiddleware(get_response)
        middleware(Mock())
        output = self.capture_output.getvalue()
        self.assertTrue("Repeated 11 times" in output, output)

    def test_query_capture_similar(self):
        middleware = QueryCaptureMiddleware(get_response)
        middleware(Mock())
        output = self.capture_output.getvalue()
        self.assertTrue("Similar 12 times" in output, output)
