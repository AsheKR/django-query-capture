"""
Middleware using [query_capture][decorators.query_capture] available in django
"""
from django_query_capture import query_capture


class QueryCaptureMiddleware:
    """
    Capture all queries that occur when one request occurs and output them to the console.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    @query_capture()
    def __call__(self, request):
        return self.get_response(request)
