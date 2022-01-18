# API Reference

It is responsible for displaying the data sent by ClassifiedQuery.<br>
By adding customized settings, processed data can be processed one more time to make the necessary output.

## BasePresenter

You can inherit this class to create a new Presenter.<br>
All you have to do is override the `print` method.<br>
[ClassifiedQuery][classify.ClassifiedQuery] It has only one attribute.<br>
Everything has a type hint.<br>
If you look at the example below how you implemented the class, you may have an idea.


--8<-- "docs/home/customize_presenter.md"


## Example

- [SimplePresenter][presenter.simple.SimplePresenter]

![simple_query_presenter.png](assets/images/api_guide/simple_query_presenter.png)

- [RawLinePresenter][presenter.raw_line.RawLinePresenter]

![raw_line_presenter.png](assets/images/api_guide/raw_line_presenter.png)

- [PrettyPresenter][presenter.pretty.PrettyPresenter]

![pretty_presenter.png](assets/images/api_guide/pretty_presenter.png)

- [OnlySlowQueryPresenter][presenter.only_slow_query.OnlySlowQueryPresenter]

![only_slow_query_presenter.png](assets/images/api_guide/only_slow_query_presenter.png)
