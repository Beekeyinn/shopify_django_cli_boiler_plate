import binascii
import os
from django.http import HttpRequest

import shopify
from django.conf import settings
from django.db.transaction import atomic
from django.urls import reverse
from shopify.utils import shop_url
import logging
from typing import Any, Tuple, Union
from accounts.models import User

from utils.shopify import get_embedded_url

logger = logging.getLogger("install")


def get_sanitized_shop_param(request: HttpRequest) -> str:
    logger.info(
        "SHOP DOMAIN CHECK: %s", request.GET.get("shop", request.POST.get("shop"))
    )
    sanitized_shop_domain = shop_url.sanitize_shop_domain(
        request.GET.get("shop", request.POST.get("shop"))
    )
    if not sanitized_shop_domain:
        raise ValueError("Shop must match 'example.myshopify.com'")
    return sanitized_shop_domain


def build_auth_params(request: HttpRequest) -> Tuple[str, str, str]:
    scopes = get_configured_scopes()
    redirect_uri = build_redirect_uri(request)
    state = build_state_param()

    return scopes, redirect_uri, state


def get_configured_scopes() -> str:
    return getattr(settings, "SHOPIFY_API_SCOPES").split(",")


def build_redirect_uri(request: HttpRequest) -> str:
    app_url = request.get_host()
    callback_path = reverse("callback")
    redirect = "https://{app_url}{callback_path}".format(
        app_url=app_url, callback_path=callback_path, shop=request.GET.get("shop")
    )
    return redirect


def build_state_param() -> str:
    return binascii.b2a_hex(os.urandom(15)).decode("utf-8")


def store_state_param(request: HttpRequest, state: str) -> None:
    request.session["shopify_oauth_state_param"] = state


def _new_session(shop_url: str) -> shopify.Session:
    shopify_api_version = getattr(settings, "SHOPIFY_API_VERSION")
    shopify_api_key = getattr(settings, "SHOPIFY_API_KEY")
    shopify_api_secret = getattr(settings, "SHOPIFY_API_SECRET")

    shopify.Session.setup(api_key=shopify_api_key, secret=shopify_api_secret)
    return shopify.Session(shop_url, shopify_api_version)


# Callback helper methods


def validate_params(request: HttpRequest, params: dict) -> None:
    validate_state_param(request, params.get("state", None))
    shopify.Session.setup(
        api_key=getattr(settings, "SHOPIFY_API_KEY"),
        secret=getattr(settings, "SHOPIFY_API_SECRET"),
    )
    if not shopify.Session.validate_params(params):  # Validates HMAC
        raise ValueError("Invalid callback parameters")


def validate_state_param(request: HttpRequest, state: str) -> None:
    if request.session.get("shopify_oauth_state_param") != state:
        raise ValueError("Anti-forgery state parameter does not match")

    request.session.pop("shopify_oauth_state_param", None)


from shopify.api_access import ApiAccess


def exchange_code_for_access_token(
    request: HttpRequest, shop: str
) -> Tuple[str, ApiAccess]:
    session = _new_session(shop)
    access_token = session.request_token(request.GET)
    access_scopes = session.access_scopes

    return access_token, access_scopes


def store_shop_information(
    access_token: str, access_scopes: ApiAccess, shop: str, host: str
) -> Union[User, None]:
    try:
        with atomic():
            user, created = User.objects.get_or_create(
                shopify_domain=shop,
            )
            user.access_scopes = access_scopes
            user.token = access_token
            user.host = host
            user.save()
            return user
    except Exception as e:
        logger.error("Exception occured while storing user information", exc_info=e)


def build_callback_redirect_uri(request: HttpRequest, params: dict):
    redirect_url = get_embedded_url(request)
    return redirect_url


# callback after_authenticate_jobs helper methods
def after_authenticate_jobs(request: HttpRequest, shop: str, access_token: str) -> None:
    create_uninstall_webhook(request, shop, access_token)


def create_uninstall_webhook(
    request: HttpRequest, shop: str, access_token: str
) -> None:
    with shopify_session(shop, access_token):  # type: ignore
        app_url = request.get_host()

        webhook = shopify.Webhook()
        webhook.topic = "app/uninstalled"
        webhook.address = "https://{host}/api/webhooks".format(host=app_url)
        webhook.format = "json"
        webhook.save()

        webhook = shopify.Webhook()
        webhook.topic = "app_subscriptions/update"
        webhook.address = "https://{host}/api/v1/shopify/billing/status/webhook".format(
            host=app_url
        )
        webhook.format = "json"
        webhook.save()


def shopify_session(shopify_domain: str, access_token: str):
    api_version = getattr(settings, "SHOPIFY_API_VERSION")

    return shopify.Session.temp(shopify_domain, api_version, access_token)


def get_backend() -> Any:
    backend = (
        getattr(settings, "SHOPIFY_BACKEND")
        if hasattr(settings, "SHOPIFY_BACKEND")
        else None
    )
    return backend
