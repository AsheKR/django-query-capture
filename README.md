# django-query-capture

[![Build status](https://github.com/ashekr/django-query-capture/workflows/build/badge.svg?branch=main&event=push)](https://github.com/ashekr/django-query-capture/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/django-query-capture.svg)](https://pypi.org/project/django-query-capture/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ashekr/django-query-capture/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ashekr/django-query-capture/blob/main/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ashekr/django-query-capture/releases)
[![License](https://img.shields.io/github/license/ashekr/django-query-capture)](https://github.com/ashekr/django-query-capture/blob/main/LICENSE)
![Coverage Report](assets/images/coverage.svg)


## Overview

![img.png](assets/images/main.png)

Django Query Capture can check the query situation at a glance, notice slow queries, and notice where N+1 occurs.

Some reasons you might want to use django-query-capture:

- It can be used to simply check queries in a specific block.
- It supports all of Django Middleware, with Context, and Decorator.
- When you use Context with Context, you can get real-time query data.
- It is easy to customize by simply changing the table shape, changing the color, and selecting and setting the desired output.
- It supports free customization that allows you to decorate the output freely from the beginning.
- It supports Type hint everywhere.

### Simple Usage

- Just add it to Middleware without any other settings, and it will be output whenever a query occurs.

```python
MIDDLEWARE = [
  ...,
  "django_query_capture.middleware.QueryCaptureMiddleware",
]
```
  
- Use in function-based views. or just function
```python
from django_query_capture import query_capture

@query_capture()
def my_view(request):
  pass
```

- Use in class-based views.
```python
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_query_capture import query_capture

@method_decorator(query_capture, name='dispatch')
class AboutView(TemplateView):
  pass
```

- Use it as a context.

When used as Context, you can check the query situation in real time.

```python
from django_query_capture import query_capture

from tests.news.models import Reporter

@query_capture()
def run_something():
    with query_capture() as capture:
        Reporter.objects.create(full_name=f"target-1")
        print(len(capture.captured_queries))  # console: 1
        Reporter.objects.create(full_name=f"target-2")
        print(len(capture.captured_queries))  # console: 2
```

## Requirements

- Python (3.8, 3.9)
- Django(3.2, 4.0)

## Installation

```bash
pip install -U django-query-capture
```

or install with `Poetry`

```bash
poetry add django-query-capture
```

## Settings

```python
QUERY_CAPTURE = {
    "PRINT_THRESHOLDS": {  # If you exceed the values below, it will be output to the console.
        "SLOW_MIN_SECOND": 1,  # time thresholds
        "DUPLICATE_MIN_COUNT": 10,  # duplicate query thresholds
        "SIMILAR_MIN_COUNT": 10,  # similar query thresholds
        "COLOR": "yellow",  # The color you want to show when you go over the thresholds.
    },
    "PRESENTER": "django_query_capture.presenter.PrettyPresenter",  # Output class, if you change this class, you can freely customize it.
    "IGNORE_SQL_PATTERNS": [],  # SQL Regex pattern list not to capture
    "PRETTY": {"TABLE_FORMAT": "pretty", "SQL_COLOR_FORMAT": "friendly"},  # Setting values that can be customized when using PrettyPresenter.
}
```

COLOR: [Available List](https://github.com/django/django/blob/main/django/utils/termcolors.py)

TABLE_FORMAT: [Available List](https://github.com/astanin/python-tabulate#table-format)

SQL_COLOR_FORMAT: [Available List](https://pygments.org/styles/)

## 🛡 License

[![License](https://img.shields.io/github/license/ashekr/django-query-capture)](https://github.com/ashekr/django-query-capture/blob/main/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ashekr/django-query-capture/blob/main/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{django-query-capture,
  author = {AsheKR},
  title = {Awesome `django-query-capture` is a Python cli/package created with https://github.com/TezRomacH/python-package-template},
  year = {2022},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ashekr/django-query-capture}}
}
```

## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)
