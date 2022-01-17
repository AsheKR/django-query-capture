# API Reference

It is responsible for displaying the data sent by ClassifiedQuery.<br>
By adding customized settings, processed data can be processed one more time to make the necessary output.

## BasePresenter

You can inherit this class to create a new Presenter.<br>
All you have to do is override the `print` method.<br>
`ClassifiedQuery`, It has only one attribute.<br>
Everything has a type hint.<br>
If you look at the example below how you implemented the class, you may have an idea.


## SimpleQueryPresenter

![simple_query_presenter.png](assets/images/api_guide/simple_query_presenter.png)

## RawLinePresenter

![raw_line_presenter.png](assets/images/api_guide/raw_line_presenter.png)

## PrettyPresenter

![pretty_presenter.png](assets/images/api_guide/pretty_presenter.png)

## OnlyLogSlowQueryPresenter

![only_log_slow_query_presenter.png](assets/images/api_guide/only_log_slow_query_presenter.png)
