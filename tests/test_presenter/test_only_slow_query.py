from django.test import TestCase, override_settings
from news.models import Reporter
from test_presenter.utils import ConsoleOutputTestCaseMixin

from django_query_capture import query_capture


@override_settings(
    QUERY_CAPTURE={
        "PRESENTER": "django_query_capture.presenter.OnlySlowQueryPresenter",
        "PRINT_THRESHOLDS": {
            "SLOW_MIN_SECOND": 0,
            "DUPLICATE_MIN_COUNT": 10,
            "SIMILAR_MIN_COUNT": 10,
            "COLOR": "yellow",
        },
    }
)
class PrettyPresenterTests(ConsoleOutputTestCaseMixin, TestCase):
    def test_print_simple(self):
        with query_capture() as q:
            [Reporter.objects.create(full_name=f"target-{i}") for i in range(1)]
