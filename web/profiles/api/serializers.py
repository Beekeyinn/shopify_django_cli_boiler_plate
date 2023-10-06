from rest_framework import serializers

from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    fullname = serializers.CharField(read_only=True)
    review_later = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = Profile
        fields = (
            "user",
            "deleted_at",
            "shop_name",
            "country",
            "email",
            "fullname",
            "created_at",
            "updated_at",
            "review_on",
            "review_later",
            "tutorial",
            "reviewed",
        )
        read_only_fields = (
            "user",
            "deleted_at",
            "shop_name",
            "country",
            "email",
            "fullname",
            "created_at",
            "updated_at",
            "review_on",
        )

    def __init__(self, *args, **kwargs):
        try:
            self.request = kwargs.get("context", {}).get("request")
        except:
            pass
        super().__init__(*args, **kwargs)

    def save(self, **kwargs):
        # kwargs["user"] = self.request.user
        return super().save(**kwargs)
