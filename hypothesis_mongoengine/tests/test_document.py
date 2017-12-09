from bson import BSON
from hypothesis import given, note
from mongoengine import Document, fields
from pytest import approx

from ..strategies import documents


class Foo(Document):
    string = fields.StringField()
    required = fields.StringField(required=True)
    choices = fields.StringField(choices=('foo', 'bar', 'baz'))
    regex = fields.StringField(regex=r'^[a-z]*$')
    length = fields.StringField(min_length=1, max_length=3)
    strings = fields.ListField(fields.StringField())
    integer = fields.IntField()
    bounded_int = fields.IntField(min_value=0, max_value=10)
    longeger = fields.LongField()
    bounded_long = fields.LongField(min_value=0, max_value=10)
    floating = fields.FloatField()
    bounded_float = fields.FloatField(min_value=0.0, max_value=1.0)
    boolean = fields.BooleanField()
    datetime = fields.DateTimeField()


@given(documents(Foo))
def test_document_validates(doc):
    note(doc.to_json())
    doc.validate()  # Throws when invalid


@given(documents(Foo))
def test_document_serializes_deserializes(doc):
    note(doc.to_json())
    son = doc.to_mongo()
    assert BSON.encode(son).decode() == approx(son.to_dict(), nan_ok=True)
