from contextlib import ContextDecorator, ExitStack

from django.db import connection


class query_capture(ContextDecorator):
    def __init__(self):
        self._exit_stack = ExitStack().__enter__()
        self.captured_queries = []

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
