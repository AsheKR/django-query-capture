import sqlparse

from django_query_capture.classify import ClassifiedQuery


class BasePresenter:
    def __init__(self, classified_query: ClassifiedQuery):
        self.classified_query = classified_query

    def print(self):
        raise NotImplementedError


class RawLinePresenter(BasePresenter):
    def print(self):
        print(
            f'\ntotal: {self.classified_query["total"]}\n'
            f'read: {self.classified_query["read"]}\n'
            f'writes: {self.classified_query["writes"]}\n'
            f'total_duration: {self.classified_query["total_duration"]}\n'
            f'most_common_duplicates: {self.classified_query["most_common_duplicates"]}\n'
            f'most_common_similar: {self.classified_query["most_common_similar"]}\n'
        )

        for query, count in self.classified_query["duplicates_counter"].items():
            print(
                f"Repeated {count} times.\n"
                f'{sqlparse.format(query, reindent=True, keyword_case="upper")}'
            )

        for query, count in self.classified_query["similar_counter"].items():
            print(
                f"Similar {count} times.\n"
                f'{sqlparse.format(query, reindent=True, keyword_case="upper")}'
            )
