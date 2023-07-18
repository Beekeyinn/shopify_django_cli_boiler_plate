from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.accounts.authentication import ShopifyAuthentication

from apps.accounts.api.serializers import UserSerializer
from apps.accounts.authentication import ShopifyAuthentication
from apps.accounts.models import User
from django.utils.decorators import method_decorator


class IdentityAPIView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [
        IsAuthenticated,
    ]
    authentication_classes = [ShopifyAuthentication]

    def get_queryset(self):
        if isinstance(self.request.user, User):
            return User.objects.prefetch_related(
                "profile", "credit", "credit__plan", "credit__plan__services"
            ).get(shopify_domain=self.request.user.shopify_domain)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
