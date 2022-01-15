from django_query_capture import query_capture


class QueryCaptureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    @query_capture()
    def __call__(self, request):
        return self.get_response(request)
