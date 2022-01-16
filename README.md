# django-query-capture

<div align="center">

[![Build status](https://github.com/ashekr/django-query-capture/workflows/build/badge.svg?branch=main&event=push)](https://github.com/ashekr/django-query-capture/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/django-query-capture.svg)](https://pypi.org/project/django-query-capture/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ashekr/django-query-capture/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ashekr/django-query-capture/blob/main/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ashekr/django-query-capture/releases)
[![License](https://img.shields.io/github/license/ashekr/django-query-capture)](https://github.com/ashekr/django-query-capture/blob/main/LICENSE)
![Coverage Report](assets/images/coverage.svg)

</div>

## Overview

Django Query Capture 는 한 눈에 쿼리 상황을 확인하고, 느린 쿼리를 알아채고, N+1 이 일어나는 곳을 알아차릴 수 있습니다.

Query Capture 를 사용해야하는 사람들

- Django 의 어느 부분에서나 간단하게 쿼리를 확인하고 싶을 때 사용합니다.
- Django Middleware, with Context 및 Decorator 를 모두 지원합니다.
- with Context 를 사용했을 때는 실시간 쿼리 데이터를 받아올 수 있습니다.
- 단순히 테이블 형태를 바꾸거나, 색을 바꾸고, 원하는 출력을 선택하여 설정해 사용하는 간편하게 커스텀하여 수 있습니다.
- 출력을 처음부터 마음대로 꾸밀 수 있는 자유로운 커스터마이징을 지원합니다. ( 커스텀 할 수 있는 문서를 지원합니다. )


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

### Simple Usage

- Middleware 를 설정하면 모든 Request 의 쿼리를 확인할 수 있습니다.

```python
MIDDLEWARE = [
  ...,
  "django_query_capture.middleware.QueryCaptureMiddleware",
]
```

- Decorator 로 사용하기

```python
from django_query_capture import query_capture

@query_capture()
def run_something():
    pass
```
  
  - 함수형 view 에서 사용하기
```python
from django_query_capture import query_capture

@query_capture()
def my_view(request):
  pass
```

  - 클래스 기반 View 에서 사용하기
```python
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django_query_capture import query_capture

@method_decorator(query_capture, name='dispatch')
class AboutView(TemplateView):
  pass
```

- Context 로 사용하기

context 로 사용했을 경우 실시간으로 캡쳐된 쿼리를 확인할 수 있습니다.

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

### Settings

```python
QUERY_CAPTURE = {
    "PRINT_THRESHOLDS": {  # 아래 값들을 초과하면 콘솔에 출력됩니다.
        "SLOW_MIN_SECOND": 1,  # 시간
        "DUPLICATE_MIN_COUNT": 10,  # 중복 개수
        "SIMILAR_MIN_COUNT": 10,  # 비슷한 중복 개수
        "COLOR": "yellow",  # 임계치를 넘었을 시 출력에 사용 할 색
    },
    "PRESENTER": "django_query_capture.presenter.PrettyPresenter",  # 콘솔에 출력하는 Presenter 클래스
    "IGNORE_SQL_PATTERNS": [],  # 캡쳐하지 않을 regex 패턴 목록
    "PRETTY": {"TABLE_FORMAT": "pretty", "SQL_COLOR_FORMAT": "friendly"},  # PrettyPresenter 를 사용했을 때 커스텀할 수 있는 세팅 값
}
```

TABLE_FORMAT: [사용 가능한 목록](https://github.com/astanin/python-tabulate#table-format)

SQL_COLOR_FORMAT: [사용 가능한 목록](https://pygments.org/styles/)



## 🛡 License

[![License](https://img.shields.io/github/license/ashekr/django-query-capture)](https://github.com/ashekr/django-query-capture/blob/main/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ashekr/django-query-capture/blob/main/LICENSE) for more details.


## Contribute first steps

### Initialize your code

1. Initialize `git` inside your repo:

```bash
cd django-query-capture && git init
```

2. If you don't have `Poetry` installed run:

```bash
make poetry-download
```

3. Initialize poetry and install `pre-commit` hooks:

```bash
make install
make pre-commit-install
```

4. Run the codestyle:

```bash
make codestyle
```

### Poetry

Want to know more about Poetry? Check [its documentation](https://python-poetry.org/docs/).

### Makefile usage

[`Makefile`](https://github.com/ashekr/django-query-capture/blob/main/Makefile) contains a lot of functions for faster development.

<details>
<summary>1. Download and remove Poetry</summary>
<p>

To download and install Poetry run:

```bash
make poetry-download
```

To uninstall

```bash
make poetry-remove
```

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

Install requirements:

```bash
make install
```

Pre-commit hooks coulb be installed after `git init` via

```bash
make pre-commit-install
```

</p>
</details>

<details>
<summary>3. Codestyle</summary>
<p>

Automatic formatting uses `pyupgrade`, `isort` and `black`.

```bash
make codestyle

# or use synonym
make formatting
```

Codestyle checks only, without rewriting files:

```bash
make check-codestyle
```

> Note: `check-codestyle` uses `isort`, `black` and `darglint` library

Update all dev libraries to the latest version using one comand

```bash
make update-dev-deps
```

</details>
<details>
<summary>4. Code security</summary>
<p>

```bash
make check-safety
```

This command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.

```bash
make check-safety
```

</p>
</details>

<details>
<summary>5. Type checks</summary>
<p>

Run `mypy` static type checker

```bash
make mypy
```

</p>
</details>

<details>
<summary>6. Tests with coverage badges</summary>
<p>

Run `pytest`

```bash
make test
```

</p>
</details>

<details>
<summary>7. All linters</summary>
<p>

Of course there is a command to ~~rule~~ run all linters in one:

```bash
make lint
```

the same as:

```bash
make test && make check-codestyle && make mypy && make check-safety
```

</p>
</details>

<details>
<summary>8. Docker</summary>
<p>

```bash
make docker-build
```

which is equivalent to:

```bash
make docker-build VERSION=latest
```

Remove docker image with

```bash
make docker-remove
```

More information [about docker](https://github.com/ashekr/django-query-capture/tree/main/docker).

</p>
</details>

<details>
<summary>9. Cleanup</summary>
<p>
Delete pycache files

```bash
make pycache-remove
```

Remove package build

```bash
make build-remove
```

Delete .DS_STORE files

```bash
make dsstore-remove
```

Remove .mypycache

```bash
make mypycache-remove
```

Or to remove all above run:

```bash
make cleanup
```

</p>
</details>

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
