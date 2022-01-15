import sys
from io import StringIO


class ConsoleOutputTestCaseMixin:
    def setUp(self) -> None:
        self.capture_output = StringIO()
        sys.stdout = self.capture_output

    def tearDown(self) -> None:
        sys.stdout = sys.__stdout__
