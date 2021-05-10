from django.db import models

# Create your models here.

class AttributeName(models.Model):
    nazev = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Nazev atributu"
    )
    kod = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Kod"
    )
    zobrazit = models.BooleanField(
    blank=True, default=False, verbose_name="Zobrazen"
    )

    def __str__(self):
        return self.nazev


class AttributeValue(models.Model):
    hodnota = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.hodnota


class Attribute(models.Model):
    nazev_atributu_id = models.ForeignKey(
    AttributeName, null=True, on_delete=models.SET_NULL,
    )
    hodnota_atributu_id = models.ForeignKey(
    AttributeValue, null=True, on_delete=models.SET_NULL,
    )


class Image(models.Model):
    obrazek = models.CharField(
    max_length=400, null=True, blank=True, verbose_name="Link obrazku"
    )


class Product(models.Model):
    CURRENCY = (
    ('CZK', 'CZK'),
    ('EUR', 'EUR')
    )

    nazev = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Nazev"
    )
    description = models.TextField(
    max_length=999, blank=True, default=None, null=True, verbose_name="Popis"
    )
    cena = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Cena"
    )
    mena = models.CharField(
    max_length=3, default=False, blank=True, choices=CURRENCY,
    verbose_name="Mena"
    )
    published_on = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Publikovano dne"
    )
    is_published = models.BooleanField(
    blank=True, default=False, verbose_name="Publikovano"
    )

    def __str__(self):
        return (self.nazev)


class ProductAttributes(models.Model):
    attribute = models.ForeignKey(
    Attribute, null=True, on_delete=models.SET_NULL,
    )
    product = models.ForeignKey(
    Product, null=True, on_delete=models.SET_NULL,
    )


class ProductImage(models.Model):
    product = models.ForeignKey(
    Product, null=True, on_delete=models.SET_NULL,
    )
    obrazek_id = models.ForeignKey(
    Image, null=True, on_delete=models.SET_NULL,
    )
    nazev = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Nazev obrazku"
    )


class Catalog(models.Model):
    nazev = models.CharField(
    max_length=200, null=True, blank=True, verbose_name="Nazev katalogu"
    )
    obrazek_id = models.ForeignKey(
    Image, null=True, on_delete=models.SET_NULL,
    )
    products_ids = models.ManyToManyField(Product, blank=True)
    attributes_ids = models.ManyToManyField(Attribute, blank=True)
