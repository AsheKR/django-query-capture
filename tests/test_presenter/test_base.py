from django.test import TestCase, override_settings
from news.models import Reporter

from django_query_capture import query_capture


class PresenterTestCases(TestCase):
    @override_settings(QUERY_CAPTURE={"PRESENTER": "no.module"})
    def test_not_exist_presenter(self):
        with self.assertRaises(ModuleNotFoundError):
            with query_capture():
                [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
