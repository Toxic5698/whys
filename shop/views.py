from django.shortcuts import render, redirect, get_object_or_404

from django.http import HttpResponse, JsonResponse, Http404

from django.contrib import messages

from django.apps import apps

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q

from django.views.generic import ListView

from rest_framework import status, generics
from rest_framework.decorators import parser_classes
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated

from .models import *
from .serializers import *
from .filters import ProductFilter
from .forms import CreateUserForm, ProductSearchForm

# Create your views here.

def registerPage(request):
    form = CreateUserForm()
    if request.user.is_authenticated:
        return redirect('detail')
    else:
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, f'Uzivatel {user} vytvoren, prihlaste se prosim.')
                return redirect('login')

        context={'form': form}
        return render(request, 'shop/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('detail')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('detail')
            else:
                messages.warning(
                request, f'Nesprávný uživatel nebo heslo, zkuste znovu.'
                )

        context={}
        return render(request, 'shop/login.html', context)


def logoutUser(request):
    logout(request)
    return redirect('login')


class Import(LoginRequiredMixin, APIView):
    """
    Import data in json.
    Transfer_dict and for loop serve transfer name of 'model' to serializer.

    """
    login_url = '/login/'
    # permission_classes = (IsAuthenticated,)
    # renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'shop/import.html'


    def get_object(self, model, pk):
        Model = apps.get_model('shop', model)
        return get_object_or_404(Model, id=pk)


    def put(self, request, format=None):
        transfer_dict = {
        'AttributeName': AttrNameSerializer,
        'AttributeValue': AttrValueSerializer,
        'Attribute': AttrSerializer,
        'ProductAttributes': ProductAttrSerializer,
        'Image': ImagesSerializer,
        'ProductImage': ProductImgSerializer,
        'Product': ProductSerializer,
        'Catalog': CatalogSerializer,
        }
        for i in request.data:
            model = ''.join(i)
            if model in transfer_dict:
                try:
                    line_id = self.get_object(model, i.get(model).get("id"))
                    serializer = transfer_dict[model](line_id, data=i.get(model))
                    if serializer.is_valid():
                        serializer.save()
                except:
                    serializer = transfer_dict[model](data=i.get(model))
                    if serializer.is_valid():
                        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Records(generics.ListAPIView):
    """
    Get list of records according model through url <modelName>.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'shop/detail.html'


    def get(self, request):
            models = apps.all_models['shop']
            return Response({'models': models})


class RecordsList(generics.ListAPIView):
    """
    Get list of records according model through url <modelName>.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'shop/detail.html'


    def get(self, request, modelName):
        models = apps.all_models['shop']
        Model = apps.get_model('shop', modelName)
        try:
            model = Model.objects.all()

            context = {
            'models': models,
            'model': model
            }
            return Response(context)
        except Model.DoesNotExist:
            raise Http404


class RecordDetail(generics.ListAPIView): #DetailView?
    """
    Get detail for record.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'shop/detail.html'


    def get(self, request, modelName, pk):
        models = apps.all_models['shop']
        Model = apps.get_model('shop', modelName)
        try:
            all_fields = Model()._meta.fields
            record = Model.objects.get(id=pk)

            context = {
            'models': models,
            'record': record,
            'all_fields': all_fields,

            }
            return Response(context)
        except Model.DoesNotExist:
            raise Http404


class ProductList(generics.ListAPIView):
    """
    Get list of products.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'shop/product.html'

    def get(self, request):

        # searching
        form = ProductSearchForm()
        q = ''
        results = []
        query = Q()
        if 'q' in request.GET:
            form = ProductSearchForm(request.GET)
            if form.is_valid():
                q = form.cleaned_data['q']
                if q is not None:
                    query &= Q(name__contains=q)


                results = Product.objects.filter(query)

        #filtering


        # rendering
        try:
            products = Product.objects.all()
            filter = ProductFilter(request.GET, queryset=products)
            product = filter.qs

            context = {
            'form': form,
            'q': q,
            'results': results,
            'products': products,
            'filter': filter
            }
            return Response(context)
        except Product.DoesNotExist:
            raise Http404
