"""
This is the [default setting](../home/settings.md) of django_query_capture.
You can adjust the threshold or change the shape of the output by referring to [settings](../home/settings.md).
"""
import typing

from functools import lru_cache

from django.conf import settings
from django.core.signals import setting_changed
from django.dispatch import receiver

CONFIG_DEFAULTS = {
    "PRINT_THRESHOLDS": {
        "SLOW_MIN_SECOND": 1,
        "DUPLICATE_MIN_COUNT": 10,
        "SIMILAR_MIN_COUNT": 10,
        "COLOR": "magenta",
    },
    "PRESENTER": "django_query_capture.presenter.PrettyPresenter",
    "IGNORE_SQL_PATTERNS": [],
    "PRETTY": {"TABLE_FORMAT": "pretty", "SQL_COLOR_FORMAT": "paraiso-light"},
}


@lru_cache
def get_config() -> typing.Dict[str, typing.Any]:
    """
    Utilities that help you use the default settings if you don't use the user
    Returns:
        Among the values of [settings](../home/settings.md), the existing value is returned.
    """
    USER_CONFIG = getattr(settings, "QUERY_CAPTURE", {})
    CONFIG = CONFIG_DEFAULTS.copy()
    CONFIG.update(USER_CONFIG)
    return CONFIG


@receiver(setting_changed)
def update_toolbar_config(*, setting, **kwargs):
    """
    Refresh configuration when overriding settings.
    """
    if setting == "QUERY_CAPTURE":
        get_config.cache_clear()
