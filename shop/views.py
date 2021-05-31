from django.shortcuts import get_object_or_404

from django.urls import reverse

from django.http import Http404

from django.conf import settings

from django.contrib.sites.shortcuts import get_current_site

from django.apps import apps

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import filters

import django_filters.rest_framework as dfrf

from rest_framework_simplejwt.tokens import RefreshToken

import jwt

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .filters import ProductFilter
from .models import User, Product
from .renderers import UserRenderer
from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    LogoutSerializer,
    AttrNameSerializer,
    AttrValueSerializer,
    AttrSerializer,
    ImagesSerializer,
    ProductSerializer,
    ProductAttrSerializer,
    ProductImgSerializer,
    CatalogSerializer,
)
from .utils import Util


# Create your views here.


class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer,)

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data["email"])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse("email-verify")
        absurl = "http://" + current_site + relativeLink + "?token=" + str(token)
        email_body = " Link pro overeni Vaseho e-mailu \n" + absurl
        data = {
            "email_body": email_body,
            "to_email": user.email,
            "email_subject": "Overeni e-mailu",
        }

        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        "token",
        in_=openapi.IN_QUERY,
        description="Description",
        type=openapi.TYPE_STRING,
    )

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY)
            user = User.objects.get(id=payload["user_id"])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({"email": "Overeno"}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"error": "Doba pro aktivaci jiz uplynula"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"error": "Spatny token"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class Import(APIView):

    # permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, model, pk):
        Model = apps.get_model("shop", model)
        return get_object_or_404(Model, id=pk)

    def put(self, request, format=None):
        transfer_dict = {
            "AttributeName": AttrNameSerializer,
            "AttributeValue": AttrValueSerializer,
            "Attribute": AttrSerializer,
            "ProductAttributes": ProductAttrSerializer,
            "Image": ImagesSerializer,
            "ProductImage": ProductImgSerializer,
            "Product": ProductSerializer,
            "Catalog": CatalogSerializer,
        }
        control_dict = {}
        for count, i in enumerate(request.data):
            model = "".join(i)
            if model in transfer_dict:
                try:
                    line_id = self.get_object(model, i.get(model).get("id"))
                    serializer = transfer_dict[model](line_id, data=i.get(model))
                    if serializer.is_valid():
                        serializer.save()
                        control_dict[count] = serializer.data
                    else:
                        serializer.is_valid()
                        control_dict[
                            f"NEULOZENO, update_fail {count}"
                        ] = serializer.errors

                except Http404:
                    serializer = transfer_dict[model](data=i.get(model))
                    if serializer.is_valid():
                        serializer.save()
                        control_dict[count] = serializer.data
                    else:
                        serializer.is_valid()
                        control_dict[
                            f"NEULOZENO, create_fail {count}"
                        ] = serializer.errors
                except AttributeError:
                    control_dict[f"NEULOZENO, wrong_data {count}"] = i
            else:
                control_dict[f"NEULOZENO, wrong_model_name {count}"] = i

        return Response(control_dict)


class RecordsList(APIView):
    def get(self, request, model_name):
        transfer_dict = {
            "AttributeName": AttrNameSerializer,
            "AttributeValue": AttrValueSerializer,
            "Attribute": AttrSerializer,
            "ProductAttributes": ProductAttrSerializer,
            "Image": ImagesSerializer,
            "ProductImage": ProductImgSerializer,
            "Product": ProductSerializer,
            "Catalog": CatalogSerializer,
        }

        try:
            model = apps.get_model("shop", model_name)
            if str(model.__name__) in transfer_dict:
                record = model.objects.all().order_by("id")
                serializer = transfer_dict[str(model.__name__)](record, many=True)
            return Response(serializer.data)
        except LookupError:
            raise Http404


class RecordDetail(APIView):
    def get(self, request, model_name, pk):
        transfer_dict = {
            "AttributeName": AttrNameSerializer,
            "AttributeValue": AttrValueSerializer,
            "Attribute": AttrSerializer,
            "ProductAttributes": ProductAttrSerializer,
            "Image": ImagesSerializer,
            "ProductImage": ProductImgSerializer,
            "Product": ProductSerializer,
            "Catalog": CatalogSerializer,
        }

        try:
            model = apps.get_model("shop", model_name)
            if str(model.__name__) in transfer_dict:
                record = model.objects.get(id=pk)
                serializer = transfer_dict[str(model.__name__)](record, many=False)
            return Response(serializer.data)
        except LookupError:
            raise Http404


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [dfrf.DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["nazev", "description"]
    filterset_class = ProductFilter
