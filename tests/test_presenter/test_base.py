from django.test import TestCase, override_settings
from news.models import Reporter
from test_presenter.utils import ConsoleOutputTestCaseMixin

from django_query_capture import query_capture


class PresenterTestCases(ConsoleOutputTestCaseMixin, TestCase):
    @override_settings(QUERY_CAPTURE={"PRESENTER": "no.module"})
    def test_not_exist_presenter(self):
        with self.assertRaises(ModuleNotFoundError):
            with query_capture():
                [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]

    @override_settings(QUERY_CAPTURE={"IGNORE_SQL_PATTERNS": ["INSERT *"]})
    def test_ignore_pattern(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
