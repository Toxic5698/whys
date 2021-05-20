from django.shortcuts import render, redirect, get_object_or_404

from django.http import Http404

from django.contrib import messages

from django.apps import apps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
import django_filters.rest_framework as dfrf
from rest_framework import filters

from .models import (
    AttributeName,
    AttributeValue,
    Attribute,
    Image,
    Product,
    ProductAttributes,
    ProductImage,
    Catalog
)
from .serializers import (
    AttrNameSerializer,
    AttrValueSerializer,
    AttrSerializer,
    ImagesSerializer,
    ProductSerializer,
    ProductAttrSerializer,
    ProductImgSerializer,
    CatalogSerializer
)
from .filters import ProductFilter
from .forms import CreateUserForm

# Create your views here.


def registerPage(request):
    form = CreateUserForm()
    if request.user.is_authenticated:
        return redirect("import")
    else:
        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get("username")
                messages.success(
                    request, f"Uzivatel {user} vytvoren, prihlaste se prosim."
                )
                return redirect("login")

        context = {"form": form}
        return render(request, "shop/register.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("import")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("import")
            else:
                messages.warning(
                    request, f"Nesprávný uživatel nebo heslo, zkuste znovu."
                )

        context = {}
        return render(request, "shop/login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


class Import(LoginRequiredMixin, APIView):
    login_url = "/login/"
    # permission_classes = (IsAuthenticated,)

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
                    serializer = transfer_dict[model](
                        line_id,
                        data=i.get(model)
                    )
                    if serializer.is_valid():
                        serializer.save()
                        control_dict[count] = serializer.data
                    else:
                        control_dict[
                            f'NEULOZENO, nespravny model {count}'
                        ] = i

                except Http404:
                    serializer = transfer_dict[model](data=i.get(model))
                    if serializer.is_valid():
                        serializer.save()
                        control_dict[count] = serializer.data
                    else:
                        control_dict[
                            f'NEULOZENO, nespravny model {count}'
                        ] = i
            else:
                control_dict[
                    f'NEULOZENO, nespravny model {count}'
                ] = i

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
                record = model.objects.all().order_by('id')
                serializer = transfer_dict[
                    str(model.__name__)
                ](record, many=True)
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
                serializer = transfer_dict[
                    str(model.__name__)
                ](record, many=False)
                items = list(serializer.data.values())
                all_fields = model()._meta.fields
                item_dict = {}
                for key in all_fields:
                    for value in items:
                        item_dict[key.verbose_name.title()] = value
                        items.remove(value)
                        break

            return Response(serializer.data)
        except LookupError:
            raise Http404


class ProductList(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        dfrf.DjangoFilterBackend,
        filters.SearchFilter
    ]
    # filterset_fields = [
    #     'productattributes__attribute__nazev_atributu_id',
    #     'productattributes__attribute__hodnota_atributu_id',
    # ]
    search_fields = ['nazev', 'description']
    filterset_class = ProductFilter
