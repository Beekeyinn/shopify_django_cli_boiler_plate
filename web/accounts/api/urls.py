from django.urls import path

from apps.accounts.api.views import IdentityAPIView

urlpatterns = [
    path("identity/", IdentityAPIView.as_view(), name="identity"),
]
