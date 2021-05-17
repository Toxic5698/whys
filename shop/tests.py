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


class TestURLs(TestCase):

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
    #         url = reverse(f"detail/{model}/{str(self.attribute.id)}")
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


class ViewsTest(TestCase):

    def set_up(self):
        self.client = Client()
        self.list_url = reverse('list')
        self.detail_url = reverse('detail')

    def test_records_list(self):
        modelNames = [
            'attribute',
            'attributename',
            'attributevalue',
            'image',
            'product',
            'catalog'
            ]
        for model in modelNames:
            client = Client()
            response = client.get(reverse('list', args=[model]))

            self.assertEquals(response.status_code, 200)
            self.assertTemplateUsed(response, 'shop/detail.html')
