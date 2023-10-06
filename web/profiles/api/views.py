import logging

from django.utils import timezone
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.accounts.authentication import ShopifyAuthentication
from apps.accounts.models import User
from apps.shopify_profile.api.serializers import ProfileSerializer
from apps.shopify_profile.models import ShopifyProfile
from base.decorator import api_exception_handler

app_name = __package__.split(".")[1]
logger = logging.getLogger(app_name)


class UserProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    authentication_classes = [ShopifyAuthentication]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ShopifyProfile.objects.filter(user=self.request.user)

    @method_decorator(api_exception_handler)
    def create(self, request: Request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @method_decorator(api_exception_handler)
    def update(self, request: Request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @method_decorator(api_exception_handler)
    def list(self, request: Request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(api_exception_handler)
    def retrieve(self, request: Request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(api_exception_handler)
    def partial_update(self, request: Request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @method_decorator(api_exception_handler)
    def destroy(self, request: Request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProfileUpdateAPIView(GenericAPIView):
    serializer_class = ProfileSerializer
    authentication_classes = [ShopifyAuthentication]

    @method_decorator(api_exception_handler)
    def post(self, request: Request, *args, **kwargs):
        user: User = getattr(request, "user")
        profile = user.profile
        datas = request.data
        for data in datas.keys():
            if data == "review_later" and datas.get(data, False):
                review_latter_date = timezone.now() + timezone.timedelta(days=2)
                setattr(profile, "review_on", review_latter_date)
            else:
                setattr(profile, data, datas.get(data, getattr(profile, data)))
        profile.save()
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
