from rest_framework import serializers

from apps.accounts.models import User
from apps.accounts.services import update_profile

PROFILE_FIELDS = (
    "salutation",
    "title",
    "first_name",
    "middle_name",
    "last_name",
    "preferred_name",
    "gender",
    "pronouns",
    "date_of_birth",
    "place_of_birth",
    "nationality",
    "phone",
    "mobile",
    "website",
    "street",
    "house_number",
    "address_line2",
    "postal_code",
    "city",
    "region",
    "country",
    "bio",
    "avatar",
    "language",
    "timezone",
)


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
            *PROFILE_FIELDS,
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
    class Meta:
        model = User
        fields = ("email", *PROFILE_FIELDS)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A user with that email address already exists.")
        return value

    def update(self, instance, validated_data):
        return update_profile(instance, validated_data)
