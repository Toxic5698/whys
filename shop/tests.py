import unittest
import json
from django.test import TestCase, Client

from django.urls import reverse, resolve

from rest_framework.test import APIRequestFactory

from .forms import CreateUserForm
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

from .serializers import (
    AttrNameSerializer,
    AttrValueSerializer,
    AttrSerializer,
    ImagesSerializer,
    ProductSerializer,
    ProductAttrSerializer,
    ProductImgSerializer,
    CatalogSerializer
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

    def test_detail(self):
        url = reverse('detail', kwargs={
            'model_name': 'attributename', 'pk': '1'
        })
        self.assertEquals(resolve(url).func.view_class, RecordDetail)

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
        )
        self.catalog.products_ids.add(Product.objects.first())

        self.view = ProductList.as_view()
        self.factory = APIRequestFactory()

    def test_get_queryset(self):
        self.assertEquals(self.attrname.nazev, 'Barva')
        self.assertEquals(self.attrvalue.hodnota, 'modra')
        self.assertEquals(self.attr.nazev_atributu_id.nazev, 'Barva')
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
        self.assertEquals(self.catalog.products_ids.first().nazev, 'Lednice')        

    def test_records_list_status_ok(self):
        model_names = [
            'attribute',
            'attributename',
            'attributevalue',
            'image',
            'product',
            'catalog',
            'productattributes',
            'productimage',
            ]
        for model in model_names:
            with self.subTest(model=model):
                response = self.client.get(reverse('list', args=[model]))
                self.assertEquals(response.status_code, 200)
                self.assertIsNot(response.data, None)


    def test_records_list_status_nok(self):
        response = self.client.get(reverse('list', args=['model']))
        self.assertEquals(response.status_code, 404)

    def test_record_detail_status_ok(self):
        model_names = [
            'attribute',
            'attributename',
            'attributevalue',
            'image',
            'catalog',
            'productattributes',
            'productimage',
            ]
        for model in model_names:
            with self.subTest(model=model):
                response = self.client.get(
                    reverse('detail', kwargs={
                        'model_name': model, 'pk': 1
                    }))
                self.assertEquals(response.status_code, 200)
                self.assertEquals(response.data['id'], 1)

    def test_record_detail_product(self):
        response = self.client.get(reverse(
            'detail', kwargs={'model_name': 'product', 'pk': 1}))
        self.assertEquals(response.data['nazev'], 'Lednice')
        # product nema dostupne id?

    def test_record_detail_status_nok(self):
        response = self.client.get(
            reverse('detail', kwargs={
                'model_name': 'model', 'pk': 2
            }))
        self.assertEquals(response.status_code, 404)

    def test_product_list_status(self):
        response = self.client.get(reverse('product'))
        self.assertEquals(response.status_code, 200)
        self.assertIsNot(response.data, None)

    def test_product_search_nazev(self):
        request = self.factory.get('/product/?search=Lednice')
        response = self.view(request)
        self.assertNotEqual(len(response.data), 0)

    def test_product_search_description(self):
        request = self.factory.get('/product/?search=prase')
        response = self.view(request)
        self.assertNotEqual(len(response.data), 0)

    def test_product_search_none(self):
        request = self.factory.get('/product/?search=bota')
        response = self.view(request)
        self.assertEqual(len(response.data), 0)

    def test_product_filter(self):
        request = self.factory.get('/product/?productattributes=1')
        response = self.view(request)
        self.assertEqual(len(response.data), 1)

    def test_import_status(self):
        request = self.factory.get(reverse('import'))
        response_factory = self.view(request)
        response_client = self.client.get(reverse('import'))
        self.assertEquals(response_factory.status_code, 200)
        self.assertEquals(response_client.status_code, 302)

    # def test_import_data(self):
    #     response = self.factory.put('import', (),
    #           {
    #             "AttributeName": {
    #               "id": 1,
    #               "nazev": "Barva"
    #             }
    #           },
    #           {
    #             "AttributeValue": {
    #               "id": 1,
    #               "hodnota": "modrá"
    #             }
    #           },
    #           {
    #             "AttributeValue": {
    #               "id": 2,
    #               "hodnota": "zelená"
    #             }
    #           }
            
    #     )
    #     self.assertEquals(json.loads(response.content), 'data')

class SerializersTest(unittest.TestCase):

    def test_fields_attributename(self):
        data = AttrNameSerializer(
            instance=AttributeName.objects.create(
                nazev='Barva',
                kod='Paint',
                zobrazit=True
            )).data

        self.assertEqual(
            set(data.keys()), 
            set(['id', 'nazev', 'kod', 'zobrazit'])
        )

    def test_fields_attributevalue(self):
        data = AttrValueSerializer(
            instance=AttributeValue.objects.create(
                hodnota='modra',
            )).data

        self.assertEqual(
            set(data.keys()), 
            set(['id', 'hodnota'])
        )

    def test_fields_attribute(self):
        data = AttrSerializer(
            instance=Attribute.objects.create(
                nazev_atributu_id=AttributeName.objects.first(),
                hodnota_atributu_id=AttributeValue.objects.first(),
            )).data

        self.assertEqual(
            set(data.keys()), 
            set(['id', 'nazev_atributu_id', 'hodnota_atributu_id'])
        )

    def test_fields_image(self):
        data = ImagesSerializer(
            instance=Image.objects.create(
                obrazek='https://free-images.com/or/4929/fridge_t_png.jpg'
            )).data

        self.assertEqual(
            set(data.keys()), 
            set(['id', 'obrazek',])
        )

    def test_fields_product(self):
        data = ProductSerializer(
            instance=Product.objects.create(
                nazev='Lednice',
                description='chladi jako prase',
                cena=2547,
                mena='CZK',
                published_on='254876325',
                is_published=True
            )).data

        self.assertEqual(
            set(data.keys()), 
            set([
                #'id', ??
                'nazev','description','cena','mena',
                'published_on', 'is_published','productimage_set', 
                'catalog_set', 'productattributes_set'
            ])
        )

    def test_fields_productattributes(self):
        data = ProductAttrSerializer(
            instance=ProductAttributes.objects.create(
                attribute=Attribute.objects.first(),
                product=Product.objects.first()
            )).data

        self.assertEqual(
            set(data.keys()), 
            set(['id', 'attribute','product',])
        )

    def test_fields_productimage(self):
        data = ProductImgSerializer(
            instance=ProductImage.objects.create(
                nazev='hlavni foto',
                product=Product.objects.first(),
                obrazek_id=Image.objects.first()
            )).data

        self.assertEqual(
            set(data.keys()), 
            set(['id', 'nazev','product', 'obrazek_id'])
        )

    def test_fields_catalog(self):
        data = CatalogSerializer(
            instance=Catalog.objects.create(
                nazev='vyprodej',
                obrazek_id=Image.objects.first(),
            )).data

        self.assertEqual(
            set(data.keys()), 
            set([
                'id', 'nazev','obrazek_id', 
                'products_ids', 'attributes_ids'])
        )





    

    

