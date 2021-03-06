from bson import BSON
from hypothesis import given, note
from mongoengine import Document, EmbeddedDocument, fields

from ..strategies import documents


class Foo(Document):
    string = fields.StringField()
    required = fields.StringField(required=True)
    choices = fields.StringField(choices=('foo', 'bar', 'baz'))
    regex = fields.StringField(regex=r'^[a-z]*$')
    length = fields.StringField(min_length=1, max_length=3)
    strings = fields.ListField(fields.StringField())
    sorted_strings = fields.SortedListField(fields.StringField())
    integer = fields.IntField()
    bounded_int = fields.IntField(min_value=0, max_value=10)
    longeger = fields.LongField()
    bounded_long = fields.LongField(min_value=0, max_value=10)
    floating = fields.FloatField()
    bounded_float = fields.FloatField(min_value=0.0, max_value=1.0)
    boolean = fields.BooleanField()
    datetime = fields.DateTimeField()
    complex_datetime = fields.ComplexDateTimeField()
    binary = fields.BinaryField()
    bounded_binary = fields.BinaryField(max_bytes=8)
    mapping = fields.MapField(fields.StringField())
    uuid = fields.UUIDField()

    old_geopoint = fields.GeoPointField()

    point = fields.PointField()
    line = fields.LineStringField()
    polygon = fields.PolygonField()

    points = fields.MultiPointField()
    lines = fields.MultiLineStringField()
    polygons = fields.MultiPolygonField()

    even_length_string = fields.StringField(
        validation=lambda s: len(s) % 2 == 0)

    @fields.EmbeddedDocumentField
    class embedded_bar(EmbeddedDocument):
        bar = fields.StringField()

    @fields.EmbeddedDocumentListField
    class embedded_baz(EmbeddedDocument):
        baz = fields.StringField()


@given(documents(Foo))
def test_document_validates(doc):
    note(doc.to_json())
    doc.validate()  # Throws when invalid


@given(documents(Foo))
def test_document_serializes_deserializes(doc):
    note(doc.to_json())
    son = doc.to_mongo()
    BSON.encode(son).decode()
    # There are some issues comparing the round-tripped version to the
    # original:
    #
    # 1) NaN != NaN, but you can store NaN in a FloatField. pytest.approx
    #    allows the test to pass, but it's a pain when the test fails because
    #    you get TypeError instead of a nice assertion.
    # 2) Binary. In Python 3, BSON deserializes Binary to bytes, but
    #    MongoEngine always casts to the bson.Binary wrapper.
