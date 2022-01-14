import typing

from collections import Counter
from contextlib import ContextDecorator, ExitStack

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
        result = execute(sql, params, many, context)
        self.captured_queries.append(
            {
                "sql": sql % tuple(params) if params else sql,
                "raw_sql": sql,
                "raw_params": params,
                "many": many,
                "context": context,
            }
        )

        return result


class ClassifiedQuery(typing.TypedDict):
    read: int
    writes: int
    total: int
    most_common_duplicates: int
    most_common_similar: int
    duplicates_counter: typing.Counter[str]
    similar_counter: typing.Counter[str]


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
