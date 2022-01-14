import typing

import time
from collections import Counter
from contextlib import ContextDecorator, ExitStack

import sqlparse
from django.db import connection
from django.db.backends.dummy.base import DatabaseWrapper
from django.db.backends.utils import CursorWrapper


class CapturedQueryContext(typing.TypedDict):
    connection: DatabaseWrapper
    cursor: CursorWrapper


class CapturedQuery(typing.TypedDict):
    sql: str
    raw_sql: str
    raw_params: str
    many: bool
    duration: float
    context: CapturedQueryContext


class query_capture(ContextDecorator):
    def __init__(self):
        self._exit_stack = ExitStack().__enter__()
        self.captured_queries: typing.List[CapturedQuery] = []

    def __enter__(self):
        self._exit_stack.enter_context(connection.execute_wrapper(self._save_queries))
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._exit_stack.close()
        self._exit_stack.__exit__(None, None, None)

    def __getattr__(self, item):
        return self.captured_queries[item]

    def __len__(self):
        return len(self.captured_queries)

    def _save_queries(self, execute, sql, params, many, context):
        start_timestamp = time.monotonic()
        result = execute(sql, params, many, context)
        duration = time.monotonic() - start_timestamp
        self.captured_queries.append(
            {
                "sql": sql % tuple(params) if params else sql,
                "raw_sql": sql,
                "raw_params": params,
                "many": many,
                "duration": duration,
                "context": context,
            }
        )

        return result


class ClassifiedQuery(typing.TypedDict):
    read: int
    writes: int
    total: int
    total_duration: float
    most_common_duplicates: int
    most_common_similar: int
    duplicates_counter: typing.Counter[CapturedQuery]
    similar_counter: typing.Counter[CapturedQuery]
    captured_queries: typing.List[CapturedQuery]


class CapturedQueryClassifier:
    def __init__(self, captured_queries: typing.List[CapturedQuery]):
        self.captured_queries = captured_queries

    def __call__(self) -> ClassifiedQuery:
        stats: ClassifiedQuery = {
            "read": self.get_read_count(),
            "writes": self.get_writes_count(),
            "total": self.get_total_count(),
            "total_duration": self.get_total_duration(),
            "most_common_duplicates": 0,
            "most_common_similar": 0,
            "duplicates_counter": self.get_duplicates_counter(),
            "similar_counter": self.get_similar_counter(),
            "captured_queries": self.captured_queries,
        }
        most_common_duplicates = stats["duplicates_counter"].most_common(1)
        if most_common_duplicates:
            sql, count = most_common_duplicates[0]
            stats["most_common_duplicates"] = count

        most_common_similar = stats["similar_counter"].most_common(1)
        if most_common_similar:
            sql, count = most_common_similar[0]
            stats["most_common_similar"] = count

        return stats

    def get_read_count(self):
        return sum(
            1
            for capture_query in self.captured_queries
            if capture_query["raw_sql"].startswith("SELECT")
        )

    def get_writes_count(self):
        return sum(
            1
            for capture_query in self.captured_queries
            if not capture_query["raw_sql"].startswith("SELECT")
        )

    def get_total_count(self):
        return len(self.captured_queries)

    def get_total_duration(self) -> float:
        return sum(capture_query["duration"] for capture_query in self.captured_queries)

    def get_duplicates_counter(self) -> typing.Counter[CapturedQuery]:
        duplicates_counter = Counter()
        for capture_query in self.captured_queries:
            if capture_query["sql"]:
                duplicates_counter[capture_query["sql"]] += 1

        return duplicates_counter

    def get_similar_counter(self) -> typing.Counter[CapturedQuery]:
        similar_counter = Counter()
        for capture_query in self.captured_queries:
            if capture_query["raw_sql"]:
                similar_counter[capture_query["raw_sql"]] += 1

        return similar_counter


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
