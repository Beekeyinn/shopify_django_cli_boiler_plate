import base64
from urllib import parse
from django.conf import settings
from django.http.request import HttpRequest
from typing import Union, TypedDict


UrlRequest = TypedDict("UrlRequest", host=str, embedded=int)


def get_embedded_url(request: Union[HttpRequest, UrlRequest]) -> str:
    if isinstance(request, HttpRequest):
        dicts = request.GET.dict()
        host = request.GET.get("host", "").encode("ascii") + b"=="
    else:
        dicts = request
        host = request.get("host").encode("ascii") + b"=="
    redirect_url = f"https://{base64.b64decode(host).decode('utf-8')}/apps/{getattr(settings,'SHOPIFY_API_KEY')}/?{parse.urlencode(dicts)}"
    return redirect_url
