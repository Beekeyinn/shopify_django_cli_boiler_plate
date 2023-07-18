from rest_framework import serializers

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    confirmation_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "is_active",
            "is_admin",
            "shopify_domain",
            "access_scopes",
            "updated_at",
            "created_at",
            "host",
            "credits",
            "profile",
            "reinstalled",
            "confirmation_url",
        )
        read_only_fields = (
            "id",
            "is_active",
            "is_admin",
            "shopify_domain",
            "host",
            "access_scopes",
            "updated_at",
            "created_at",
            "credits",
            "profile",
            "reinstalled",
            "confirmation_url",
        )
