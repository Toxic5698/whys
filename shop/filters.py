from django_filters import rest_framework as filters
from .models import Product, ProductAttributes


class ProductFilter(filters.FilterSet):
    productattributes = filters.ModelChoiceFilter(
        queryset=ProductAttributes.objects.all()
    )

    class Meta:
        model = Product
        fields = [
            "productattributes",
        ]

        # provazani mezi Attribute pres ProductAttributes do Product
