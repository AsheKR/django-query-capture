import sys
from io import StringIO

from django.test import TestCase, override_settings
from news.models import Reporter

from django_query_capture import query_capture


@override_settings(
    QUERY_CAPTURE={"PRESENTER": "django_query_capture.presenter.pretty.PrettyPresenter"}
)
class PrettyPresenterTests(TestCase):
    def setUp(self) -> None:
        self.capture_output = StringIO()
        sys.stdout = self.capture_output

    def tearDown(self) -> None:
        sys.stdout = sys.__stdout__

    def test_print_pretty(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(1)]

    def test_print_pretty_duplicate(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-i") for i in range(11)]
        output = self.capture_output.getvalue()
        self.assertTrue("Repeated" in output)

    def test_print_pretty_similar(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
        output = self.capture_output.getvalue()
        self.assertTrue("Similar" in output)
