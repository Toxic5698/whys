from django.contrib import auth

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import (
    User,
    AttributeName,
    AttributeValue,
    Attribute,
    Image,
    Product,
    ProductAttributes,
    ProductImage,
    Catalog,
)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    default_error_messages = {
        "username": "Uzivatelske jmeno by nemelo obsahovat specialni znaky."
    }

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        username = attrs.get("username", "")

        if not username.isalnum():
            raise serializers.ValidationError(self.default_error_messages)
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)

    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = User.objects.get(email=obj["email"])

        return {"refresh": user.tokens()["refresh"], "access": user.tokens()["access"]}

    class Meta:
        model = User
        fields = ["email", "password", "username", "tokens"]

    def validate(self, attrs):
        email = attrs.get("email", "")
        password = attrs.get("password", "")
        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Nespravne prihlasovaci udaje, zkuste znovu.")
        if not user.is_active:
            raise AuthenticationFailed("Ucet zablokovan.")
        if not user.is_verified:
            raise AuthenticationFailed("Neprobehlo overeni pres e-mail.")

        return {"email": user.email, "username": user.username, "tokens": user.tokens}

        return super().validate(attrs)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_message = {"bad_token": ("Token vyprsel nebo je vadny.")}

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()

        except TokenError:
            self.fail("bad_token")


class AttrNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeName
        fields = "__all__"


class AttrValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeValue
        fields = "__all__"


class AttrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = "__all__"


class ProductAttrSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributes
        fields = "__all__"


class ImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = "__all__"


class ProductImgSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "nazev",
            "description",
            "cena",
            "mena",
            "published_on",
            "is_published",
        ]
