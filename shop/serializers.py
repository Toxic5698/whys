from rest_framework import serializers
from .models import *


class AttrNameSerializer(serializers.ModelSerializer):
    # name = serializers.CharField(source="nazev")
    # code = serializers.CharField(source='kod')
    # show = serializers.BooleanField(source='zobrazit')


    class Meta:
        model = AttributeName
        fields = '__all__'


class AttrValueSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttributeValue
        fields = '__all__'


class AttrSerializer(serializers.ModelSerializer):
    # name = AttrNameSerializer(many=True)
    # value = AttrValueSerializer(many=True)

    class Meta:
        model = Attribute
        fields = '__all__'

class ProductAttrSerializer(serializers.ModelSerializer):
    #attr = AttrSerializer(many=True)

    class Meta:
        model = ProductAttributes
        fields = '__all__'


class ImagesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = '__all__'


class ProductImgSerializer(serializers.ModelSerializer):
    # img_id = ImagesSerializer(many=True)

    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    # images = ProductImgSerializer(many=True)
    # attrs = ProductAttrSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'


class CatalogSerializer(serializers.ModelSerializer):
    # products = ProductSerializer(many=True)

    class Meta:
        model = Catalog
        fields = '__all__'
        extra_kwargs = {'products': {'required': False}}
