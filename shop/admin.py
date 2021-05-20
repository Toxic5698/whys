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


class ProductAttributesInline(admin.StackedInline):
    model = ProductAttributes


class ProductImageInline(admin.TabularInline):
    model = ProductImage


class ProductAdmin(admin.ModelAdmin):
    list_display = ('nazev', 'is_published', 'description')
    list_filter = ('is_published', 'productattributes__attribute')
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
    ]
    inlines = [
        ProductAttributesInline, ProductImageInline
    ]


admin.site.register(AttributeName)
admin.site.register(AttributeValue)
admin.site.register(Attribute)
admin.site.register(Image)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductAttributes)
admin.site.register(ProductImage)
admin.site.register(Catalog)
