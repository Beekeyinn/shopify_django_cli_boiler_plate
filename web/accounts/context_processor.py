from typing import Any, Dict
from django.conf import settings
from django.http import HttpRequest

from accounts.models import User


def get_authenticated_user(request: HttpRequest) -> Dict[str, Any]:
    if isinstance(request.user, User):
        return {
            "shopify": {
                "shopify_domain": request.user.shopify_domain,
                "domain_prefix": str(request.user.shopify_domain).split(
                    ".", maxsplit=2
                )[0],
                "host": request.user.host,
                "app_key": getattr(settings, "SHOPIFY_API_KEY"),
            },
            "debug": getattr(settings, "DEBUG"),
        }
    else:
        return {
            "shopify": {
                "shopify_domain": request.GET.get("shop", None),
                "domain_prefix": str(request.GET.get("shop", None)).split(
                    ".", maxsplit=2
                )[0],
                "host": request.GET.get("host", None),
                "app_key": getattr(settings, "SHOPIFY_API_KEY"),
            },
            "debug": getattr(settings, "DEBUG"),
        }
