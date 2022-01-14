import typing

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
    duplicates_counter: typing.Counter[str]
    similar_counter: typing.Counter[str]
    captured_queries: typing.List[CapturedQuery]


def classify_captured_query(
    captured_queries: typing.List[CapturedQuery],
) -> ClassifiedQuery:
    duplicates_counter = Counter()
    similar_counter = Counter()
    stats: ClassifiedQuery = {
        "read": 0,
        "writes": 0,
        "total": 0,
        "most_common_duplicates": 0,
        "most_common_similar": 0,
        "duplicates_counter": duplicates_counter,
        "similar_counter": similar_counter,
        "captured_queries": captured_queries,
    }
    for capture_query in captured_queries:
        if capture_query["raw_sql"].startswith("SELECT"):
            stats["read"] += 1
        else:
            stats["writes"] += 1
        stats["total"] += 1
        if capture_query["sql"]:
            duplicates_counter[capture_query["sql"]] += 1
        similar_counter[capture_query["raw_sql"]] += 1

        duplicates = duplicates_counter.most_common(1)
        if duplicates:
            sql, count = duplicates[0]
            stats["most_common_duplicates"] = count

        similar = similar_counter.most_common(1)
        if similar:
            sql, count = similar[0]
            stats["most_common_similar"] = count

    return stats


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
