from rest_framework import serializers
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
    productattributes_set = ProductAttrSerializer(many=True)
    productimage_set = ProductImgSerializer(many=True)
    catalog_set = CatalogSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            'nazev', 'description', 'cena', 'mena',
            'published_on', 'is_published',
            'productattributes_set', 'productimage_set', 'catalog_set'
        ]
