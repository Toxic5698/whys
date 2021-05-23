from django.db import models

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError("Doplnte uzivatelske jmeno")
        if email is None:
            raise TypeError("Doplnte e-mail")

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError("Doplte heslo")

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}


class AttributeName(models.Model):
    nazev = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Nazev atributu"
    )
    kod = models.CharField(max_length=200, null=True, blank=True, verbose_name="Kod")
    zobrazit = models.BooleanField(blank=True, default=False, verbose_name="Zobrazen")

    def __str__(self):
        return self.nazev


class AttributeValue(models.Model):
    hodnota = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Hodnota"
    )

    def __str__(self):
        return self.hodnota


class Attribute(models.Model):
    nazev_atributu_id = models.ForeignKey(
        AttributeName,
        null=True,
        on_delete=models.SET_NULL,
    )
    hodnota_atributu_id = models.ForeignKey(
        AttributeValue,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.nazev_atributu_id.nazev},\
        {self.hodnota_atributu_id.hodnota} "


class Image(models.Model):
    obrazek = models.CharField(
        max_length=400, null=True, blank=True, verbose_name="Link obrazku"
    )

    def __str__(self):
        return self.obrazek


class Product(models.Model):
    CURRENCY = (("CZK", "CZK"), ("EUR", "EUR"))

    nazev = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Nazev"
    )
    description = models.TextField(
        max_length=999, blank=True, default=None, null=True, verbose_name="Popis"
    )
    cena = models.CharField(max_length=200, null=True, blank=True, verbose_name="Cena")
    mena = models.CharField(
        max_length=3, default=False, blank=True, choices=CURRENCY, verbose_name="Mena"
    )
    published_on = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Publikovano dne"
    )
    is_published = models.BooleanField(
        blank=True, default=False, verbose_name="Publikovano"
    )

    def __str__(self):
        return self.nazev


class ProductAttributes(models.Model):
    attribute = models.ForeignKey(
        Attribute,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Atribut ID",
        related_name="productattributes",
    )
    product = models.ForeignKey(
        Product, null=True, on_delete=models.SET_NULL, verbose_name="Produkt ID"
    )

    def __str__(self):
        return f"{self.product.nazev},\
            {self.attribute.nazev_atributu_id.nazev},\
            {self.attribute.hodnota_atributu_id.hodnota} "


class ProductImage(models.Model):
    nazev = models.CharField(
        max_length=200, null=True, blank=True, verbose_name="Nazev obrazku"
    )
    product = models.ForeignKey(
        Product, null=True, on_delete=models.SET_NULL, verbose_name="Produkt ID"
    )
    obrazek_id = models.ForeignKey(
        Image, null=True, on_delete=models.SET_NULL, verbose_name="Obrazek ID"
    )

    def __str__(self):
        return f"{self.product.nazev},\
            {self.nazev}"


class Catalog(models.Model):
    nazev = models.CharField(
        max_length=200, null=True, default="Katalog", verbose_name="Nazev katalogu"
    )
    obrazek_id = models.ForeignKey(
        Image, null=True, on_delete=models.SET_NULL, verbose_name="Obrazek ID"
    )
    products_ids = models.ManyToManyField(
        Product, blank=True, verbose_name="Produkt ID"
    )
    attributes_ids = models.ManyToManyField(
        Attribute, blank=True, verbose_name="Atribut ID"
    )

    def __str__(self):
        return self.nazev
