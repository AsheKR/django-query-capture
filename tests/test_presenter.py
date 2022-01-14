from django.test import TestCase
from news.models import Reporter

from django_query_capture import RawLinePresenter, query_capture
from django_query_capture.classify import CapturedQueryClassifier


class RawLinePresenterTests(TestCase):
    def test_print(self):
        with query_capture() as q:
            [Reporter.objects.create(full_name="target-i") for i in range(10)]
            RawLinePresenter(CapturedQueryClassifier(q.captured_queries)()).print()
