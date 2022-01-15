from django.conf import settings
from django.utils import termcolors

from django_query_capture.settings import CONFIG_DEFAULTS


def get_value_from_django_settings(key):
    return getattr(settings, key, CONFIG_DEFAULTS[key])


def colorize(value: str, is_warning: bool) -> str:
    if is_warning:
        return termcolors.make_style(fg="yellow")(value)
    return value
