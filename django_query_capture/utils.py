from django.utils import termcolors

from django_query_capture.capture import CapturedQuery
from django_query_capture.settings import get_config


def colorize(value: str, is_warning: bool) -> str:
    """
    Utility to set a color for the output string when it exceeds the threshold.

    Args:
        value: String to be output.
        is_warning: Whether it exceeds the threshold.

    Returns:
        colorized string output
    """
    if is_warning:
        return termcolors.make_style(fg=get_config()["PRINT_THRESHOLDS"]["COLOR"])(  # type: ignore
            value
        )
    return value


def get_stack_prefix(captured_query: CapturedQuery) -> str:
    """
    Utilities that help you output call stacks consistently in [CapturedQuery][capture.CapturedQuery].
    Args:
        captured_query: [CapturedQuery][capture.CapturedQuery]
    """
    return f'[{captured_query["function_name"]}, {captured_query["file_name"]}:{captured_query["line_no"]}]'


def truncate_string(value: str, length: int) -> str:
    """

    Args:
        value: String to be output.
        length: Number of strings to output.

    Returns:
        truncated string
    """
    return (value[:length] + "..") if len(value) > length else value
