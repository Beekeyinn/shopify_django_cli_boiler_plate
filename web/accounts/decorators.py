import logging
from typing import Any, Union
from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect
from django.urls import reverse
from shopify import ApiAccess, Session, session_token

from accounts.models import User
from accounts.utils import get_sanitized_shop_param
from accounts.authentication import authenticate
from accounts.authentication import client_side_redirect

HTTP_AUTHORIZATION_HEADER = "HTTP_AUTHORIZATION"
logger = logging.getLogger("install")


def session_token_required(func) -> Union[Any, HttpResponse]:
    def wrapper(*args, **kwargs):
        try:
            decoded_session_token = session_token.decode_from_header(
                authorization_header=authorization_header(args[0]),
                api_key=getattr(settings, "SHOPIFY_API_KEY"),
                secret=getattr(settings, "SHOPIFY_API_SECRET"),
            )

            with shopify_session(decoded_session_token, args[0]):
                return func(*args, **kwargs)
        except session_token.SessionTokenError:
            return HttpResponse(status=401)

    return wrapper


def shopify_session(session_token: dict, request: HttpRequest):
    shopify_domain = session_token.get("dest", "").removeprefix("https://")
    setattr(request, "shopify_domain", shopify_domain)
    api_version = getattr(settings, "SHOPIFY_API_VERSION")
    access_token = User.objects.get(shopify_domain=shopify_domain).token
    setattr(request, "access_token", access_token)
    setattr(request, "api_version", api_version)
    return Session.temp(shopify_domain, api_version, access_token)


def authorization_header(request) -> str:
    return request.META.get(HTTP_AUTHORIZATION_HEADER, "")


def known_shop_required(
    func,
) -> Union[Any, Union[HttpResponseRedirect, HttpResponsePermanentRedirect]]:
    def wrapper(*args, **kwargs):
        request = args[1]
        try:
            check_shop_domain(request, kwargs)
            check_shop_known(request, kwargs)
            return func(*args, **kwargs)
        except User.DoesNotExist as dne:
            return authenticate(request)
        except Exception as e:
            return client_side_redirect(request)

    return wrapper


def check_shop_domain(request: HttpRequest, kwargs: dict) -> None:
    kwargs["shopify_domain"] = get_sanitized_shop_param(request)


def check_shop_known(request: HttpRequest, kwargs: dict) -> None:
    user = User.objects.get(shopify_domain=kwargs.get("shopify_domain"))

    kwargs["shop"] = user
    if user.host != request.GET.get("host"):
        kwargs["shop"].host = request.GET.get("host")
        kwargs["shop"].save()


def latest_access_scopes_required(
    func,
) -> Union[Any, Union[HttpResponsePermanentRedirect, HttpResponseRedirect]]:
    def wrapper(*args, **kwargs):
        request = args[1]
        try:
            configured_access_scopes = getattr(settings, "SHOPIFY_API_SCOPES")
            current_access_scopes = kwargs["shop"].access_scopes
            assert ApiAccess(configured_access_scopes) == ApiAccess(
                current_access_scopes
            )
        except Exception as e:
            redirect_url = f"https://{request.get_host()}{reverse('update')}?shop={request.GET.get('shop')}"
            url = f"https://{request.get_host()}/ExitIframe?host={request.GET.get('host')}&redirectUri={redirect_url}"
            logger.info("URL: %s", url)
            return redirect(url)
        return func(*args, **kwargs)

    return wrapper
