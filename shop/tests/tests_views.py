from django.urls import reverse

from rest_framework.test import APIRequestFactory, APIClient, APITestCase

from faker import Faker

from ..models import (
    User,
    AttributeName,
    AttributeValue,
    Attribute,
    Image,
    Product,
    ProductAttributes,
    ProductImage,
    Catalog,
)
from ..views import (
    ProductList,
)


class ViewsTest(APITestCase):
    def setUp(self):
        self.apiclient = APIClient()
        self.view = ProductList.as_view()
        self.factory = APIRequestFactory()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.import_url = reverse("import")
        self.fake = Faker()

        self.user_data = {
            "email": self.fake.email(),
            "username": self.fake.email().split("@")[0],
            "password": self.fake.email(),
        }

        self.user = User.objects.create(
            username="testuser25",
            email="testuser25@user.cz",
            password="strongpassword25",
        )

        self.attrname = AttributeName.objects.create(
            nazev="Barva", kod="Paint", zobrazit=True
        )

        self.attrvalue = AttributeValue.objects.create(
            hodnota="modra",
        )
        self.attr = Attribute.objects.create(
            nazev_atributu_id=AttributeName.objects.first(),
            hodnota_atributu_id=AttributeValue.objects.first(),
        )
        self.image = Image.objects.create(
            obrazek="https://free-images.com/or/4929/fridge_t_png.jpg"
        )
        self.product = Product.objects.create(
            nazev="Lednice",
            description="chladi jako prase",
            cena=2547,
            mena="CZK",
            published_on="254876325",
            is_published=True,
        )
        self.productattrs = ProductAttributes.objects.create(
            attribute=Attribute.objects.first(), product=Product.objects.first()
        )

        self.productimg = ProductImage.objects.create(
            nazev="hlavni foto",
            product=Product.objects.first(),
            obrazek_id=Image.objects.first(),
        )
        self.catalog = Catalog.objects.create(
            nazev="vyprodej",
            obrazek_id=Image.objects.first(),
        )
        self.catalog.products_ids.add(Product.objects.first())
        self.catalog.attributes_ids.add(Attribute.objects.first())

    def test_get_queryset(self):
        self.assertEquals(self.attrname.nazev, "Barva")
        self.assertEquals(self.attrvalue.hodnota, "modra")
        self.assertEquals(self.attr.nazev_atributu_id.nazev, "Barva")
        self.assertEquals(self.attr.hodnota_atributu_id.hodnota, "modra")
        self.assertEquals(
            self.image.obrazek, "https://free-images.com/or/4929/fridge_t_png.jpg"
        )
        self.assertEquals(self.product.nazev, "Lednice")
        self.assertEquals(self.productattrs.attribute.nazev_atributu_id.nazev, "Barva")
        self.assertEquals(self.productattrs.product.nazev, "Lednice")
        self.assertEquals(self.productimg.nazev, "hlavni foto")
        self.assertEquals(self.productimg.product.nazev, "Lednice")
        self.assertEquals(
            self.productimg.obrazek_id.obrazek,
            "https://free-images.com/or/4929/fridge_t_png.jpg",
        )
        self.assertEquals(self.catalog.nazev, "vyprodej")
        self.assertEquals(
            self.catalog.obrazek_id.obrazek,
            "https://free-images.com/or/4929/fridge_t_png.jpg",
        )
        self.assertEquals(self.catalog.products_ids.first().nazev, "Lednice")
        self.assertEquals(
            self.catalog.attributes_ids.first().nazev_atributu_id.nazev, "Barva"
        )

    def test_user_register_without_data(self):
        response = self.apiclient.post(self.register_url)
        self.assertEqual(response.status_code, 400)

    def test_user_register_ok(self):
        response = self.apiclient.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.data["email"], self.user_data["email"])
        self.assertEqual(response.data["username"], self.user_data["username"])
        self.assertEqual(response.status_code, 201)

    def test_user_login_without_username(self):
        response = self.apiclient.post(
            self.login_url, {"password": "passwped", "username": ""}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_user_login_without_password(self):
        response = self.apiclient.post(
            self.login_url, {"username": "passwped", "password": ""}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_user_login_unverified(self):
        self.apiclient.post(self.register_url, self.user_data, format="json")
        response = self.apiclient.post(self.login_url, self.user_data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_user_login_verified(self):
        response1 = self.apiclient.post(
            self.register_url, self.user_data, format="json"
        )
        email = response1.data["email"]
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        response2 = self.apiclient.post(self.login_url, self.user_data, format="json")
        self.assertEqual(response2.status_code, 200)

    def test_records_list_status_ok(self):
        model_names = [
            "attribute",
            "attributename",
            "attributevalue",
            "image",
            "product",
            "catalog",
            "productattributes",
            "productimage",
        ]
        for model in model_names:
            with self.subTest(model=model):
                response = self.apiclient.get(reverse("list", args=[model]))
                self.assertEquals(response.status_code, 200)
                self.assertIsNot(response.data, None)

    def test_records_list_status_nok(self):
        response = self.apiclient.get(reverse("list", args=["model"]))
        self.assertEquals(response.status_code, 404)

    def test_record_detail_status_attributename(self):
        response = self.apiclient.get(
            reverse(
                "detail", kwargs={"model_name": "attributename", "pk": self.attrname.id}
            )
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_attributevalue(self):
        response = self.apiclient.get(
            reverse(
                "detail",
                kwargs={"model_name": "attributevalue", "pk": self.attrvalue.id},
            )
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_attribute(self):
        response = self.apiclient.get(
            reverse("detail", kwargs={"model_name": "attribute", "pk": self.attr.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_image(self):
        response = self.apiclient.get(
            reverse("detail", kwargs={"model_name": "image", "pk": self.image.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_product(self):
        response = self.apiclient.get(
            reverse("detail", kwargs={"model_name": "product", "pk": self.product.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_productimage(self):
        response = self.apiclient.get(
            reverse(
                "detail",
                kwargs={"model_name": "productimage", "pk": self.productimg.id},
            )
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_productattributes(self):
        response = self.apiclient.get(
            reverse(
                "detail",
                kwargs={"model_name": "productattributes", "pk": self.productattrs.id},
            )
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_catalog(self):
        response = self.apiclient.get(
            reverse("detail", kwargs={"model_name": "catalog", "pk": self.catalog.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_record_detail_status_wrong_model(self):
        response = self.apiclient.get(
            reverse("detail", kwargs={"model_name": "model", "pk": 2})
        )
        self.assertEquals(response.status_code, 404)

    def test_product_list_status_ok(self):
        response = self.apiclient.get(reverse("product"))
        self.assertEquals(response.status_code, 200)
        self.assertIsNot(response.data, None)

    def test_product_search_nazev(self):
        request = self.factory.get("/product/?search=Lednice")
        response = self.view(request)
        self.assertNotEqual(len(response.data), 0)

    def test_product_search_description(self):
        request = self.factory.get("/product/?search=prase")
        response = self.view(request)
        self.assertNotEqual(len(response.data), 0)

    def test_product_search_none(self):
        request = self.factory.get("/product/?search=bota")
        response = self.view(request)
        self.assertEqual(len(response.data), 0)

    def test_product_filter(self):
        request = self.factory.get("/product/?productattributes=1")
        response = self.view(request)
        self.assertEqual(len(response.data), 1)

    def test_import_status(self):
        request = self.factory.get(reverse("import"))
        response_factory = self.view(request)
        self.assertEquals(response_factory.status_code, 200)

    def test_import_data_ok(self):
        self.import_data = [
            {"AttributeName": {"id": 1, "nazev": "Barva"}},
            {"AttributeValue": {"id": 1, "hodnota": "modrá"}},
            {
                "Image": {
                    "id": 1,
                    "obrazek": "https://free-images.com/or/4929/fridge_t_png.jpg",
                }
            },
        ]

        self.apiclient.force_authenticate(user=self.user)
        response = self.apiclient.put(self.import_url, self.import_data, format="json")
        self.assertEquals(response.data[0]["nazev"], "Barva")
        self.assertEquals(response.data[1]["hodnota"], "modrá")
        self.assertEquals(
            response.data[2]["obrazek"],
            "https://free-images.com/or/4929/fridge_t_png.jpg",
        )

    def test_import_data_wrong_model(self):
        self.import_data = [
            {"WrongModel": {"id": 1, "nazev": "Barva"}},
            {"AttributeValue": {"id": 1, "hodnota": "modrá"}},
            {"AttributeValue": {"id": 2, "hodnota": "zelená"}},
        ]

        self.apiclient.force_authenticate(user=self.user)
        response = self.apiclient.put(self.import_url, self.import_data, format="json")
        self.assertIn("NEULOZENO, wrong_model_name 0", response.data.keys())
        self.assertEquals(response.data[1]["hodnota"], "modrá")
        self.assertEquals(response.data[2]["hodnota"], "zelená")

    def test_import_data_wrong_data(self):
        self.import_data = {"AttributeValue": {"id": 1, "hodnota": "modrá"}}
        self.apiclient.force_authenticate(user=self.user)
        response = self.apiclient.put(self.import_url, self.import_data, format="json")
        self.assertIn("NEULOZENO, wrong_data 0", response.data.keys())
