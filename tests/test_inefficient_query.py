from django.test import TestCase
from news.models import Reporter
from test_presenter.utils import ConsoleOutputTestCaseMixin

from django_query_capture.test_utils import AssertInefficientQuery, assert_inefficient_query


class AssertInefficientQueryTests(ConsoleOutputTestCaseMixin, TestCase):
    def test_assert_inefficient_query(self):
        with self.assertRaises(AssertionError):
            with AssertInefficientQuery(199, 0):
                [list(Reporter.objects.all()) for i in range(200)]
                [Reporter.objects.create(full_name=f"reporter-{i}") for i in range(200)]

    @assert_inefficient_query(200)
    def test_assert_inefficient_query_with_decorator(self):
        [list(Reporter.objects.all()) for i in range(200)]
        [Reporter.objects.create(full_name=f"reporter-{i}") for i in range(200)]
