from django.test import TestCase, override_settings
from news.models import Reporter

from django_query_capture import query_capture


class QueryCaptureTests(TestCase):
    @override_settings(
        PRESENTER="django_query_capture.presenter.pretty.PrettyPresenter"
    )
    def test_print_pretty(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]

    def test_print_raw_line(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-i") for i in range(11)]

    @override_settings(PRESENTER="no.module")
    def test_not_exist_presenter(self):
        with self.assertRaises(ModuleNotFoundError):
            with query_capture():
                [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
