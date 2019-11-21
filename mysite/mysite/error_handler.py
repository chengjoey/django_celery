from mysite.exceptions import ApiError
from django.http import JsonResponse



class ExceptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_exception(self, request, exception):
        if isinstance(exception, ApiError):
            return JsonResponse({"msg":"", "value":[], "errors":exception.errors}, status=exception.http_code)
        else:
            return JsonResponse({"msg":"", "value":[], "errors":str(exception)}, status=400)