from django.test import TestCase, override_settings
from news.models import Reporter
from test_presenter.utils import ConsoleOutputTestCaseMixin

from django_query_capture import query_capture


@override_settings(
    QUERY_CAPTURE={"PRESENTER": "django_query_capture.presenter.pretty.PrettyPresenter"}
)
class PrettyPresenterTests(ConsoleOutputTestCaseMixin, TestCase):
    def test_print_pretty(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(1)]

    def test_print_pretty_duplicate(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-i") for i in range(11)]
        output = self.capture_output.getvalue()
        self.assertFalse("Similar 11 times" in output, output)
        self.assertTrue("Repeated 11 times" in output, output)

    def test_print_pretty_similar(self):
        with query_capture():
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(11)]
        output = self.capture_output.getvalue()
        self.assertTrue("Similar 11 times" in output, output)
