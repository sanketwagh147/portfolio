from . import models


def RequestObjectMiddleware(get_response):
    # initial configuration

    def middleware(request):
        # middle ware is code which is executed before each request
        # the view > middle ware is called
        models.request_object = request
        response = get_response(request)
        return response

    return middleware
