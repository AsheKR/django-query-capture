import typing

from django.conf import settings

from django_query_capture.settings import CONFIG_DEFAULTS


def get_value_from_django_settings(key):
    return getattr(settings, key, CONFIG_DEFAULTS[key])
