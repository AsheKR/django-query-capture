# API Reference

It plays a role in capturing raw data and where the query occurred when the query first occurred.<br>
Just put data and do nothing. It can be used as Decorator with Context.<br>
In the entire flow, CapturedQuery receives the data and sends it to ClassifiedQuery.<br>
Classified data can be displayed in the Presenter.

## CapturedQuery

A `data class` that adds the time and place of occurrence to the data that comes out when you capture Query in django.<br>
How to extract this data class will be described [below](#native_query_capture).


| name          	| description                                                                                                                                                                            	| example                                                       	|
|---------------	|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|---------------------------------------------------------------	|
| sql           	| SQL to which parameters are applied                                                                                                                                                    	| `'INSERT INTO "news_reporter" ("full_name") VALUES (target-1)'` 	|
| raw_sql       	| SQL to which parameters are not applied                                                                                                                                                	| `'INSERT INTO "news_reporter" ("full_name") VALUES (%s)'`       	|
| raw_params    	| Parameters to be used for SQL                                                                                                                                                          	| `['target-1']`                                                  	|
| many          	| a bool indicating whether the ultimately invoked call is `execute()` or `executemany()` (and whether params is expected to be a sequence of values, or a sequence of sequences of values). 	| `False`                                                         	|
| duration      	| Query execution time.                                                                                                                                                                  	| `4.712500000003672e-05`                                         	|
| file_name     	| The file where the query was executed.                                                                                                                                                 	| `'test_native_query_capture.py'`                                	|
| function_name 	| A function in which the query was executed.                                                                                                                                            	| `'test_capture_query_in_context_manager'`                       	|
| line_no       	| Row number where the query was executed.                                                                                                                                               	| `16`                                                            	|
| context       	| a dictionary with further data about the context of invocation. This includes the connection and cursor.                                                                               	|                                                               	|

## CapturedQueryContext

a dictionary with further data about the context of invocation. This includes the connection and cursor.<br>
For more information, please check the [official document of Django](https://docs.djangoproject.com/en/3.2/topics/db/instrumentation/#database-instrumentation).

## native_query_capture

Both Context and Decorator are supported, but nothing happens when used as a Decorator.<br>
If you use it as Context, you can use the content of [CapturedQuery](#capturedquery).

## query_capture

The highest level of module.<br>
It is a module responsible for both query capture, classification, and output.

It has both low-level [CapturedQuery](#capturedquery) data and [ClassifiedQuery][classify.ClassifiedQuery] data.<br>
Real-time data can only be obtained when used as Context Manager.


### Example

???+ example "Decorator"
    ```python
    from django_query_capture import query_capture

    @query_capture()
    def my_view(request):
      pass
    ```

???+ example "Context Manager"
    ```python
    from django_query_capture import query_capture

    with query_capture() as capture:
        Reporter.objects.create(full_name=f"target-1")
        print(len(capture.captured_queries))  # console: 1
    ```
