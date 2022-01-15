CONFIG_DEFAULTS = {
    "PRINT_THRESHOLDS": {
        "SLOW_MIN_TIME": 1,
        "DUPLICATE_MIN_COUNT": 10,
        "SIMILAR_MIN_COUNT": 10,
    },
    "PRESENTER": "django_query_capture.presenter.RawLinePresenter",
    "IGNORE_SQL_PATTERNS": [],
    "IGNORE_REQUEST_PATTERNS": [],
    "PRETTY": {"TABLE_FORMAT": "pretty", "SQL_COLOR_FORMAT": "friendly"},
}
