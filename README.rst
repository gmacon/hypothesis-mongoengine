Hypothesis Strategy for MongoEngine
===================================

This package contains a `Hypothesis <http://hypothesis.works/>`_ strategy for generating example documents from a `MongoEngine <http://mongoengine.org/>`_ model.

Here's a minimal example::

    from hypothesis import given, note
    from hypothesis_mongoengine.strategies import documents
    from mongoengine import Document, StringField


    class Foo(Document):
        foo = StringField()


    @given(documents(Foo))
    def test_something(foo):
        # Handy since the default __repr__ is unhelpful:
        note(foo.to_json())

        assert hasattr(foo, 'id')


You can customize the generation of examples by passing alternate strategies for each field as keyword arguments::

    @given(documents(Foo, foo=strategies.strings(max_size=7)))
    def test_another thing(foo):
        pass

By default, all examples that would validate against the built-in MongoEngine restrictions are generated.
If the field is not required, ``None`` will also be generated.
If ``choices`` is specified, only those values will be generated.

If ``validation`` is specified, the default strategy will be filtered by the validation function.
If the custom validation function accepts too few values, Hypothesis may fail the health check.
In that case, supply a custom validator that generates acceptable examples more efficiently.

What's Not Supported
--------------------

``ReferenceField`` is not generically supported and probably will never be.
You can, and should, provide an application-specific strategy for these fields.
This permits you to ensure that the referential-integrity constraints needed by your application are satisfied.
Don't forget that MongoEngine expects the documents to have been saved to the database before you try to reference them.

``DynamicDocument`` (and ``DynamicEmbeddedDocument``) currently generate only the explicitly-specified fields.

``DynamicField`` is normally used internally by ``DynamicDocument``,
but if you have a model which references it explicitly, it won't by handled generically.

Handling Custom Fields
----------------------

If you have a custom field in use in your application,
you can register a strategy to generate examples for it using the ``field_strat`` decorator.

For example, a strategy for the ``EnumField`` from `extras-mongoengine <https://github.com/MongoEngine/extras-mongoengine>`_ could look like this::

    from extras_mongoengine.fields import EnumField
    from hypothesis import strategies
    from hypothesis_mongoengine import field_strat

    @field_strat(EnumField)
    def my_custom_strat(field):
        return strategies.sampled_from(field.enum)

The fields are looked up in the registry by their names,
so if you have a hierarchy of custom fields, you must register the leaf types.
You can, however, stack the decorator several times if you need to::

    from extras_mongoengine.fields import EnumField, IntEnumField, StringEnumField
    from hypothesis import strategies
    from hypothesis_mongoengine import field_strat

    @field_strat(EnumField)
    @field_strat(IntEnumField)
    @field_strat(StringEnumField)
    def my_custom_strat(field):
        return strategies.sampled_from(field.enum)
