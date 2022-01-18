## How to Customize Presenter

Let's define a presenter that simply outputs the location of the query that occurs the most.

### Create a class that inherits the [BasePresenter][presenter.base.BasePresenter].

```python
from django_query_capture.presenter import BasePresenter


class MostQueryLocationPresenter(BasePresenter):
    pass
```

### Refer to the property of [ClassifiedQuery][classify.ClassifiedQuery] to get the most common similar.

Refined properties refer to [ClassifiedQuery][classify.ClassifiedQuery], and individual properties such as sql and duration refer to [ClassifiedQuery][classify.ClassifiedQuery]'s [CapturedQuery][capture.CapturedQuery].

```python
from django_query_capture.presenter import BasePresenter


class MostSimilarQueryLocationPresenter(BasePresenter):
  def print(self):
    captured_query, counter = self.classified_query['most_common_similar'][0]  # Get the counters of the most duplicated items. (Refer to typehint).
    if captured_query:
        print(f'[{captured_query["function_name"]}, {captured_query["file_name"]}:{captured_query["line_no"]}], duplicates {counter} times.')
```


### Import the Presenter defined in Settings.

```python
# settings.py

QUERY_CAPTURE = {
  ...,
  "PRESENTER": "some.path.MostQuerySimilarLocationPresenter",
}
```

### It's done!

```python
from django_query_capture import  query_capture

from news.models import Reporter

@query_capture()
def some_view():
    for reporter in Reporter.objects.all():
        for article in reporter.article_set.all():
            # ...

# Output
# [some_function, some_path.py:50], similar 20 times.
```
