from hypothesis import given
from mongoengine import Document, ReferenceField

from ..helpers import mark_saved
from ..strategies import documents


class Target(Document):
    pass


class Source(Document):
    target = ReferenceField(Target)


@given(documents(Source, target=documents(Target).map(mark_saved)))
def test_marked_saved_useable_as_reference(source):
    source.validate()
