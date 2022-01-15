from django.test import TestCase
from news.models import Reporter

from django_query_capture import RawLinePresenter, native_query_capture, query_capture
from django_query_capture.classify import CapturedQueryClassifier


class RawLinePresenterTests(TestCase):
    def test_print(self):
        with native_query_capture() as q:
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
            RawLinePresenter.print(CapturedQueryClassifier(q.captured_queries)())
