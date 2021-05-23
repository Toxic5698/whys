from django.urls import reverse, resolve

from rest_framework.test import APITestCase

from ..views import (
    RegisterView,
    VerifyEmail,
    LoginAPIView,
    LogoutAPIView,
    Import,
    RecordsList,
    RecordDetail,
    ProductList,
)


class TestURLs(APITestCase):
    def test_register(self):
        url = reverse("register")
        self.assertEquals(resolve(url).func.view_class, RegisterView)

    def test_verify_email(self):
        url = reverse("email-verify")
        self.assertEquals(resolve(url).func.view_class, VerifyEmail)

    def test_login(self):
        url = reverse("login")
        self.assertEquals(resolve(url).func.view_class, LoginAPIView)

    def test_logout(self):
        url = reverse("logout")
        self.assertEquals(resolve(url).func.view_class, LogoutAPIView)

    def test_import(self):
        url = reverse("import")
        self.assertEquals(resolve(url).func.view_class, Import)

    def test_list(self):
        url = reverse("list", args=["attribute"])
        self.assertEquals(resolve(url).func.view_class, RecordsList)

    def test_detail(self):
        url = reverse("detail", kwargs={"model_name": "attributename", "pk": "1"})
        self.assertEquals(resolve(url).func.view_class, RecordDetail)

    def test_product(self):
        url = reverse("product")
        self.assertEquals(resolve(url).func.view_class, ProductList)
