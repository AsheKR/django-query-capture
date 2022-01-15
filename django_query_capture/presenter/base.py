from django_query_capture.classify import ClassifiedQuery


class BasePresenter:
    @staticmethod
    def print(classified_query: ClassifiedQuery):
        raise NotImplementedError
