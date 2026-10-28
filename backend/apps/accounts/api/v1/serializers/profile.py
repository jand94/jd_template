from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.services import update_profile
from apps.accounts.services.accounts import PROFILE_UPDATE_FIELDS


class UserSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True, allow_null=True)
    is_email_verified = serializers.BooleanField(read_only=True)
    is_phone_verified = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            *PROFILE_UPDATE_FIELDS,
            "age",
            "is_email_verified",
            "is_phone_verified",
            "email_verified_at",
            "phone_verified_at",
            "terms_accepted_at",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ("email", *PROFILE_UPDATE_FIELDS)

    def validate_email(self, value):
        normalized = User.objects.normalize_email((value or "").strip()).casefold()
        if User.objects.filter(email=normalized).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with that email address already exists.")
        return normalized

    def update(self, instance, validated_data):
        return update_profile(instance, validated_data)
