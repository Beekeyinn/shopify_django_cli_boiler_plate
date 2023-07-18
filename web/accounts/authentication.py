import logging
from typing import Tuple, Union
from urllib import parse
from wsgiref.util import request_uri
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponsePermanentRedirect, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import authentication, exceptions
from rest_framework.authentication import CSRFCheck, SessionAuthentication
from shopify import session_token
from accounts.models import User
from accounts.utils import (
    _new_session,
    build_auth_params,
    get_sanitized_shop_param,
    store_state_param,
)

HTTP_AUTHORIZATION_HEADER = "HTTP_AUTHORIZATION"

logger = logging.getLogger("app")


def authorization_header(request):
    return request.META.get(HTTP_AUTHORIZATION_HEADER)


class ShopifyAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request) -> Tuple[User, None]:
        # Removing webhook from authorization from shopifyAuthenticatedFetch
        if getattr(settings, "DEBUG") and "swagger" in request.META.get(
            "HTTP_REFERER", request.path
        ):
            user = User.objects.get(shopify_domain=getattr(settings, "ADMIN_DOMAIN"))
        else:
            try:
                decoded_session_token = session_token.decode_from_header(
                    authorization_header=authorization_header(request),
                    api_key=getattr(settings, "SHOPIFY_API_KEY"),
                    secret=getattr(settings, "SHOPIFY_API_SECRET"),
                )
            except Exception as e:
                raise exceptions.AuthenticationFailed("Requires Shopify based request.")

            shopify_domain = decoded_session_token.get("dest").removeprefix("https://")
            try:
                user = User.objects.get(shopify_domain=shopify_domain)
            except User.DoesNotExist:
                raise exceptions.AuthenticationFailed("User not found")
        # self.enforce_csrf(request)
        return (user, None)

    def enforce_csrf(self, request: HttpRequest) -> None:
        def dummy_get_response(request):
            return None

        check = CSRFCheck(dummy_get_response)  # type:ignore
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied("CSRF Failed: %s" % reason)


def authenticate(
    request: HttpRequest, url=False
) -> Union[HttpResponsePermanentRedirect, HttpResponseRedirect]:
    try:
        shop = get_sanitized_shop_param(request)
        scopes, redirect_uri, state = build_auth_params(request)
        store_state_param(request, state)
        permission_url = _new_session(shop).create_permission_url(
            scopes, redirect_uri, state
        )
        return redirect(permission_url)
    except (ValueError, Exception) as exception:
        messages.error(request, str(exception))
        return client_side_redirect(request)


def client_side_redirect(
    request: HttpRequest,
) -> Union[HttpResponsePermanentRedirect, HttpResponseRedirect]:
    REDIRECT = f"https://{request.get_host()}{reverse('update')}?shop={request.GET.get('shop')}"
    redirect_url = f"https://{request.get_host()}/ExitIFrame?host={request.GET.get('host')}&redirectUri={REDIRECT}"
    return redirect(redirect_url)


class CsrfExemptAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return
