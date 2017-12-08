import math

from bson import BSON
from hypothesis import given, note
from mongoengine import Document, fields

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


def recursive_eq_including_nan(a, b):
    if type(a) != type(b):
        return False

    if isinstance(a, dict):
        if a.keys() != b.keys():
            return False
        return all(recursive_eq_including_nan(a[k], b[k]) for k in a)

    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(recursive_eq_including_nan(x, y) for x, y in zip(a, b))

    if isinstance(a, float) and math.isnan(a) and math.isnan(b):
        return True

    return a == b


@given(documents(Foo))
def test_document_serializes_deserializes(doc):
    note(doc.to_json())
    son = doc.to_mongo()
    assert recursive_eq_including_nan(BSON.encode(son).decode(), son.to_dict())
