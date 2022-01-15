from django.utils import termcolors

from django_query_capture import get_config


def colorize(value: str, is_warning: bool) -> str:
    if is_warning:
        return termcolors.make_style(fg=get_config()["PRINT_THRESHOLDS"]["COLOR"])(
            value
        )
    return value
