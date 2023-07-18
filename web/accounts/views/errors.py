from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_not_found_error(request: HttpRequest, exception: Exception) -> HttpResponse:
    context = {}
    response = render(request, "errors/page_404.html", context)
    response.status_code = 404
    return response


def server_error(request: HttpRequest) -> HttpResponse:
    context = {}
    response = render(request, "errors/page_500.html", context)
    response.status_code = 500
    return response


def bad_request_error(request: HttpRequest, exception: Exception) -> HttpResponse:
    context = {}
    response = render(request, "errors/page_400.html", context)
    response.status_code = 400
    return response


def permission_denied(request: HttpRequest, exception: Exception) -> HttpResponse:
    context = {}
    response = render(request, "errors/page_403.html", context)
    response.status_code = 403
    return response


def shopify_payment_error(request: HttpRequest) -> HttpResponse:
    return render(request, "errors/shopify_payment_error.html")
