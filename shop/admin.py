from django.contrib import admin
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

def make_published(modeladmin, request, queryset):
    queryset.update(is_published=True)
make_published.short_description = "Mark selected products as published"


# class ProductAttributesAdmin(admin.ModelAdmin):
#     list_display = ('nazev_atributu_id', 'hodnota_atributu_id')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'is_published', 'description')
    search_fields = ['nazev', 'description']
    actions = [make_published]
    fieldsets = [
        ('Zakladni udaje',{'fields': [
            'nazev',
            'description',
            'cena',
            'mena',
            'published_on',
            'is_published']}
        ),
        # ('Attributy', {'fields': ['product.productattributes_set.all']})
    ]


admin.site.register(AttributeName)
admin.site.register(AttributeValue)
admin.site.register(Attribute)
admin.site.register(Image)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttributes,
#    ProductAttributesAdmin
)
admin.site.register(ProductImage)
admin.site.register(Catalog)
