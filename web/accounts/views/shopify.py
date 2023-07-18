import json
import logging
from typing import Union

from django.contrib import messages
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponsePermanentRedirect,
    HttpResponseRedirect,
)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from accounts.authentication import authenticate
from accounts.models import User
from accounts.utils import (
    after_authenticate_jobs,
    build_callback_redirect_uri,
    exchange_code_for_access_token,
    store_shop_information,
    validate_params,
)
from django.views.decorators.clickjacking import xframe_options_exempt

logger = logging.getLogger("install")


class UpdateAPPView(View):
    @xframe_options_exempt
    def get(
        self, request: HttpRequest, *args, **kwargs
    ) -> Union[HttpResponsePermanentRedirect, HttpResponseRedirect]:
        return authenticate(request)


def callback(request: HttpRequest):
    params = request.GET.dict()
    shop = request.GET.get("shop", "")
    host = request.GET.get("host", "")
    try:
        validate_params(request, params)
        access_token, access_scopes = exchange_code_for_access_token(request, shop)
    except ValueError as exception:
        logger.error("Exception error in call back", exc_info=exception)
        messages.error(request, str(exception))
        return redirect(reverse("login"))
    else:
        store_shop_information(access_token, access_scopes, shop, host)
        after_authenticate_jobs(request, shop, access_token)
    finally:
        redirect_uri = build_callback_redirect_uri(request, params)
        return redirect(redirect_uri)


@csrf_exempt
def uninstall(request):
    uninstall_data = json.loads(request.body)
    logger.error(f"Uninstall View POST ->>>>>>>>>>>>>>>>>{uninstall_data}")
    shop = uninstall_data.get("domain")
    user = User.objects.filter(shopify_domain=shop)
    user.delete()
    return HttpResponse(status=204)
