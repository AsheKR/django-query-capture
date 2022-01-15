from django.conf import settings
from django.utils import termcolors

from django_query_capture.settings import CONFIG_DEFAULTS


def get_value_from_django_settings(key):
    return getattr(settings, key, CONFIG_DEFAULTS[key])


def colorize(value, is_warning):
    if is_warning:
        return termcolors.make_style(fg="yellow")(value)
    return value
