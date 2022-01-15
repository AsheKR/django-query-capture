from django.test import TestCase
from news.models import Reporter

from django_query_capture import query_capture


class QueryCaptureTests(TestCase):
    def test_print(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
