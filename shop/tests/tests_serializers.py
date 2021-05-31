from rest_framework.test import APITestCase

from ..models import (
    AttributeName,
    AttributeValue,
    Attribute,
    Image,
    Product,
    ProductAttributes,
    ProductImage,
    Catalog,
)

from ..serializers import (
    AttrNameSerializer,
    AttrValueSerializer,
    AttrSerializer,
    ImagesSerializer,
    ProductSerializer,
    ProductAttrSerializer,
    ProductImgSerializer,
    CatalogSerializer,
)


class SerializersTest(APITestCase):
    def test_fields_attributename(self):
        data = AttrNameSerializer(
            instance=AttributeName.objects.create(
                nazev="Barva", kod="Paint", zobrazit=True
            )
        ).data

        self.assertEqual(set(data.keys()), {"id", "nazev", "kod", "zobrazit"})

    def test_fields_attributevalue(self):
        data = AttrValueSerializer(
            instance=AttributeValue.objects.create(
                hodnota="modra",
            )
        ).data

        self.assertEqual(set(data.keys()), {"id", "hodnota"})

    def test_fields_attribute(self):
        data = AttrSerializer(
            instance=Attribute.objects.create(
                nazev_atributu_id=AttributeName.objects.first(),
                hodnota_atributu_id=AttributeValue.objects.first(),
            )
        ).data

        self.assertEqual(
            set(data.keys()), {"id", "nazev_atributu_id", "hodnota_atributu_id"})

    def test_fields_image(self):
        data = ImagesSerializer(
            instance=Image.objects.create(
                obrazek="https://free-images.com/or/4929/fridge_t_png.jpg"
            )
        ).data

        self.assertEqual(
            set(data.keys()),
            set(
                [
                    "id",
                    "obrazek",
                ]
            ),
        )

    def test_fields_product(self):
        data = ProductSerializer(
            instance=Product.objects.create(
                nazev="Lednice",
                description="chladi jako prase",
                cena=2547,
                mena="CZK",
                published_on="254876325",
                is_published=True,
            )
        ).data

        self.assertEqual(
            set(data.keys()),
            set(
                [
                    "nazev",
                    "description",
                    "cena",
                    "mena",
                    "published_on",
                    "is_published",
                ]
            ),
        )

    def test_fields_productattributes(self):
        data = ProductAttrSerializer(
            instance=ProductAttributes.objects.create(
                attribute=Attribute.objects.first(), product=Product.objects.first()
            )
        ).data

        self.assertEqual(
            set(data.keys()),
            set(
                [
                    "id",
                    "attribute",
                    "product",
                ]
            ),
        )

    def test_fields_productimage(self):
        data = ProductImgSerializer(
            instance=ProductImage.objects.create(
                nazev="hlavni foto",
                product=Product.objects.first(),
                obrazek_id=Image.objects.first(),
            )
        ).data

        self.assertEqual(
            set(data.keys()), {"id", "nazev", "product", "obrazek_id"})

    def test_fields_catalog(self):
        data = CatalogSerializer(
            instance=Catalog.objects.create(
                nazev="vyprodej",
                obrazek_id=Image.objects.first(),
            )
        ).data

        self.assertEqual(
            set(data.keys()),
            {"id", "nazev", "obrazek_id", "products_ids", "attributes_ids"})
