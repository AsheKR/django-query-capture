from django.utils import termcolors

from django_query_capture.capture import CapturedQuery
from django_query_capture.settings import get_config


def colorize(value: str, is_warning: bool) -> str:
    if is_warning:
        return termcolors.make_style(fg=get_config()["PRINT_THRESHOLDS"]["COLOR"])(
            value
        )
    return value


def get_stack_prefix(captured_query: CapturedQuery):
    return f'[{captured_query["function_name"]}, {captured_query["file_name"]}:{captured_query["line_no"]}]'


def truncate_string(data: str, length: int):
    return (data[:length] + "..") if len(data) > length else data
