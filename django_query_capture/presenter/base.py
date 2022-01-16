from django_query_capture.classify import ClassifiedQuery


class BasePresenter:
    def __init__(self, classified_query: ClassifiedQuery):
        self.classified_query = classified_query

    def print(self) -> None:
        raise NotImplementedError
