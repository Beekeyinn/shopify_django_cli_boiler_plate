from django.urls import include, path
from rest_framework.routers import SimpleRouter

from profiles.api.views import ProfileUpdateAPIView, UserProfileViewSet

router = SimpleRouter()
router.register(r"", UserProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
    path("update", ProfileUpdateAPIView.as_view(), name="profile-update-view"),
]
