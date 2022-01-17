# API Reference

## AssertInefficientQuery

If the Duplicate, Similar, and Slow queries exceed the specified values, it is a test utility that fails.

### Usage

| name            | description                                                                        | available value                                                |
|-----------------|------------------------------------------------------------------------------------|----------------------------------------------------------------|
| test_case       | In Class-based TestCase, put self.                                                 | All instances that inherited `django.test.testcases.TestCase`  |
| num             | If the duplication, Similar threshold, and query exceed num, the test fails.       | `Optional[int]`                                                          |
| seconds         | If the query exceeds the specified time, the test fails.                           | `Optional[int]`                                                          |
| ignore_patterns | This is a list of SQL Patterns to ignore.This is a list of SQL Patterns to ignore. | `List[str]`                                                    |

### Example

???+ example "assert Duplicate or Similar"
    ```python
    from django.test import TestCase
      from django_query_capture.test_utils import AssertInefficientQuery


    class AssertInefficientQueryTests(TestCase):
      def test_assert_inefficient_query(self):
        with AssertInefficientQuery(self, num=19):
          self.client.get('/api/reporter')  # /api/reporter duplicate query: 20, so raise error
    ```

???+ example "assert Slow"
    ```python
    from django.test import TestCase
      from django_query_capture.test_utils import AssertInefficientQuery


    class AssertInefficientQueryTests(TestCase):
      def test_assert_inefficient_query(self):
        with AssertInefficientQuery(self, seconds=1):
          self.client.get('/api/reporter')  # /api/reporter api took more than a second. so raise error
    ```
