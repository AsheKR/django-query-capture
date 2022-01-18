from django_query_capture.classify import ClassifiedQuery


class BasePresenter:
    """
    This is the parent value that can be set to [PRESENTER](../../home/settings.md) setting.<br>
    You can use the [classified_query][classify.ClassifiedQuery] attribute to determine the output.<br>
    The output can be completed by overriding the print method using the [classified_query][classify.ClassifiedQuery] attributes.
    """

    def __init__(self, classified_query: ClassifiedQuery):
        self.classified_query = classified_query

    def print(self) -> None:
        raise NotImplementedError
