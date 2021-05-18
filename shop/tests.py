import unittest
from django.test import TestCase, Client

from django.urls import reverse, resolve

from .forms import CreateUserForm, ProductSearchForm
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
from .views import (
    registerPage,
    loginPage,
    logoutUser,
    Import,
    RecordsList,
    RecordDetail,
    ProductList,
)


class TestURLs(unittest.TestCase):

    def test_register(self):
        url = reverse('register')
        self.assertEquals(resolve(url).func, registerPage)

    def test_login(self):
        url = reverse('login')
        self.assertEquals(resolve(url).func, loginPage)

    def test_logout(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, logoutUser)

    def test_import(self):
        url = reverse('import')
        self.assertEquals(resolve(url).func.view_class, Import)

    def test_list(self):

        url = reverse('list', args=['attribute'])
        self.assertEquals(resolve(url).func.view_class, RecordsList)

    # def test_detail(self):
    #     self.attribute = AttributeName.objects.create(
    #         nazev='Barva',
    #         kod='Paint',
    #         zobrazit=True
    #     )
    #     modelNames = [
    #         # 'attribute',
    #         'attributename',
    #         # 'attributevalue',
    #         # 'image',
    #         # 'product',
    #         # 'catalog'
    #         ]
    #
    #     for model in modelNames:
    #         url = reverse(f"/detail/{model}/{str(self.attribute.id)}")
    #         self.assertEquals(resolve(url).func.view_class, RecordsDetail)

    def test_product(self):
        url = reverse('product')
        self.assertEquals(resolve(url).func.view_class, ProductList)


class FormsTest(TestCase):

    def test_create_user_valid(self):
        form = CreateUserForm(data={
            'username': 'jan',
            'email': 'jan@jan.cz',
            'password1': 'Najnaj258',
            'password2': 'Najnaj258',
        })
        self.assertTrue(form.is_valid())

    def test_create_user_invalid_password(self):
        form = CreateUserForm(data={
            'username': 'jan',
            'email': 'jan@jan.cz',
            'password1': 'Najnaj258',
            'password2': 'Najnaj369',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_create_user_invalid_email(self):
        form = CreateUserForm(data={
            'username': 'jan',
            'email': 'jan',
            'password1': 'Najnaj258',
            'password2': 'Najnaj258',
        })
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 1)

    def test_create_user_no_data(self):
        form = CreateUserForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEquals(len(form.errors), 3)


class ViewsTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.attrname = AttributeName.objects.create(
            nazev='Barva',
            kod='Paint',
            zobrazit=True
        )
        self.attrvalue = AttributeValue.objects.create(
            hodnota='modra',
        )
        self.attr = Attribute.objects.create(
            nazev_atributu_id=AttributeName.objects.first(),
            hodnota_atributu_id=AttributeValue.objects.first(),
        )
        self.image = Image.objects.create(
            obrazek='https://free-images.com/or/4929/fridge_t_png.jpg'
        )
        self.product = Product.objects.create(
            nazev='Lednice',
            description='chladi jako prase',
            cena=2547,
            mena='CZK',
            published_on='254876325',
            is_published=True
        )
        self.productattrs = ProductAttributes.objects.create(
            attribute=Attribute.objects.first(),
            product=Product.objects.first()
        )

        self.productimg = ProductImage.objects.create(
            nazev='hlavni foto',
            product=Product.objects.first(),
            obrazek_id=Image.objects.first()
        )
        self.catalog = Catalog.objects.create(
            nazev='vyprodej',
            obrazek_id=Image.objects.first(),
            # products_ids=[1]
        )

    def test_records_list_status(self):
        modelNames = [
            'attribute',
            'attributename',
            'attributevalue',
            'image',
            'product',
            'catalog'
            ]
        for model in modelNames:
            with self.subTest(model=model):
                response = self.client.get(reverse('list', args=[model]))
                self.assertEquals(response.status_code, 200)

    def test_get_queryset(self):
        self.assertEquals(self.attrname.nazev, 'Barva')
        self.assertEquals(self.attrvalue.hodnota, 'modra')
        self.assertEquals(self.attr.nazev_atributu_id.id, 1)
        self.assertEquals(self.attr.hodnota_atributu_id.id, 1)
        self.assertEquals(self.image.obrazek, 'https://free-images.com/or/4929/fridge_t_png.jpg')
        self.assertEquals(self.product.nazev, 'Lednice')
        self.assertEquals(self.productattrs.attribute.id, 1)
        self.assertEquals(self.productattrs.product.id, 1)
        self.assertEquals(self.productimg.nazev, 'hlavni foto')
        self.assertEquals(self.productimg.product.id, 1)
        self.assertEquals(self.productimg.obrazek_id.id, 1)
        self.assertEquals(self.catalog.nazev, 'vyprodej')
        self.assertEquals(self.catalog.obrazek_id.id, 1)

    # def test_record_detail_status(self):
    #     modelNames = [
    #         'attribute',
    #         'attributename',
    #         'attributevalue',
    #         'image',
    #         'product',
    #         'catalog'
    #         ]
    #     for model in modelNames:
    #         with self.subTest(model=model):
    #             response = self.client.get(
    #                 reverse(f"/detail/{model}/1/"
    #                 ))
    #             self.assertEquals(response.status_code, 200)

    def test_product_list_status(self):
        response = self.client.get(reverse('product'))
        self.assertEquals(response.status_code, 200)
