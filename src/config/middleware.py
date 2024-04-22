import logging


class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        response = self.get_response(request)
        self.log_message(request, response)

        return response

    def log_message(self, request, response):
        logger = logging.getLogger('access_log')

        response_message = f"IP: {request.META.get('REMOTE_ADDR')}, \tMethod: {request.method}, \tURL: {request.get_full_path()}, \tResponse Code: {response.status_code}"

        logger.debug(response_message)