import logging
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt

from accounts.decorators import known_shop_required, latest_access_scopes_required
from django.conf import settings


logger = logging.getLogger("app")


class HomeView(View):
    @xframe_options_exempt  # type: ignore
    @known_shop_required
    @latest_access_scopes_required
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if getattr(settings, "DEBUG"):
            context = {
                "frontend_port": getattr(settings, "FRONTEND_PORT"),
                "host": getattr(settings, "HOST_URL"),
                "debug": True,
            }
        else:
            context = {}
        logger.info("HOME CONTEXT: %s", context)
        return render(request, "index.html", context)
