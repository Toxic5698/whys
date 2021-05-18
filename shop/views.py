from django.shortcuts import render, redirect, get_object_or_404

from django.http import Http404

from django.contrib import messages

from django.contrib.postgres.search import (
    TrigramSimilarity,
    SearchQuery,
    SearchRank,
    SearchVector
)
# for proper functionality of TrigramSimilarity is needed to add to postgres
# CREATE EXTENSION pg_trgm; from postgresql-contrib
from itertools import chain

from django.apps import apps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated

from django_filters import rest_framework as filters

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
from .forms import CreateUserForm, ProductSearchForm, ImportDataForm

# Create your views here.


def registerPage(request):
    form = CreateUserForm()
    if request.user.is_authenticated:
        return redirect("product")
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
        return redirect("product")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("product")
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
    """
    Import data in json.
    Transfer_dict and for loop serve transfer name of 'model' to serializer.

    """

    login_url = "/login/"
    # permission_classes = (IsAuthenticated,)
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'shop/import.html'

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

        for i in request.data:
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
                except Http404:
                    serializer = transfer_dict[model](data=i.get(model))
                    if serializer.is_valid():
                        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RecordsList(APIView):
    """
    Get list of records according model through url <modelName>.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "shop/detail.html"

    def get(self, request, modelName):
        Model = apps.get_model("shop", modelName)
        try:
            model = Model.objects.all().order_by("id")

            context = {"model": model, "modelName": modelName}
            return Response(context)
        except Model.DoesNotExist:
            raise Http404


class RecordDetail(APIView):
    """
    Get detail for record.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "shop/detail.html"

    def get(self, request, modelName, pk):
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
        Model = apps.get_model("shop", modelName)

        try:
            if str(Model.__name__) in transfer_dict:
                record = Model.objects.get(id=pk)
                serializer = transfer_dict[
                    str(Model.__name__)
                ](record, many=False)
                items = list(serializer.data.values())
                all_fields = Model()._meta.fields
                item_dict = {}
                for key in all_fields:
                    for value in items:
                        item_dict[key.verbose_name.title()] = value
                        items.remove(value)
                        break

            context = {
                "modelName": modelName,
                "record": record,
                "all_fields": all_fields,
                "item_dict": item_dict,
            }
            return Response(context)
        except Model.DoesNotExist:
            raise Http404


class ProductList(APIView):
    """
    Get list of products.
    """

    renderer_classes = [TemplateHTMLRenderer]
    template_name = "shop/product.html"

    serializer_class = ProductSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get(self, request):
        products = Product.objects.all()

        # searching
        form = ProductSearchForm()
        q = ""
        results = []
        if "q" in request.GET:
            form = ProductSearchForm(request.GET)
            if form.is_valid():
                q = form.cleaned_data["q"]
                if q is not None:
                    vector = SearchVector('description', weight='A')
                    query = SearchQuery(q)
                    nazev_search = Product.objects.annotate(
                        similarity=TrigramSimilarity('nazev', q)
                        ).filter(similarity__gt=0.1).order_by('-similarity')
                    description_search = Product.objects.annotate(
                            rank=SearchRank(vector, query)
                        ).filter(rank__gte=0.1).order_by('-rank')
                    results = set(chain(nazev_search, description_search))

        # filtering

        # rendering
        context = {
            "form": form,
            "q": q,
            "results": results,
            "products": products,
        }
        return Response(context)


class ProductDetail(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'shop/product_detail.html'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response({'serializer': serializer, 'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'product': product})
        serializer.save()
        return redirect('product')
