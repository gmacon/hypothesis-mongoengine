Hypothesis Strategy for MongoEngine
===================================

.. image:: https://travis-ci.org/gmacon/hypothesis-mongoengine.svg?branch=master

This package contains a `Hypothesis <http://hypothesis.works/>`_ strategy for generating example documents from a `MongoEngine <http://mongoengine.org/>`_ model.

Here's a minimal example:

.. code:: python

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


You can customize the generation of examples by passing alternate strategies for each field as keyword arguments:

.. code:: python

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
You can use the ``hypothesis_mongoengine.helpers.mark_saved`` function to make a document appear as if saved.

``DictField`` is not generically supported and probably will never be.
``MapField`` is supported generically and should be preferred to ``DictField`` when the values are homogenous.
When writing custom strategies for a ``DictField``,
you can use the ``hypothesis_mongoengine.strategies.mongodb_keys`` strategy to generate the keys in the absence of more specific application knowledge about the keys.

``DynamicDocument`` (and ``DynamicEmbeddedDocument``) currently generate only the explicitly-specified fields.

``DynamicField`` is normally used internally by ``DynamicDocument``,
but if you have a model which references it explicitly, it won't be handled generically.

Handling Custom Fields
----------------------

If you have a custom field in use in your application,
you can register a strategy to generate examples for it using the ``field_strat`` decorator.

For example, a strategy for the ``EnumField`` from `extras-mongoengine <https://github.com/MongoEngine/extras-mongoengine>`_ could look like this:

.. code:: python

    from extras_mongoengine.fields import EnumField
    from hypothesis import strategies
    from hypothesis_mongoengine.strategies import field_strat

    @field_strat(EnumField)
    def my_custom_strat(field):
        return strategies.sampled_from(field.enum)

The fields are looked up in the registry by equality of the classes,
so if you have a hierarchy of custom fields, you must register the leaf types.
You can, however, stack the decorator several times if you need to:

.. code:: python

    from extras_mongoengine.fields import EnumField, IntEnumField, StringEnumField
    from hypothesis import strategies
    from hypothesis_mongoengine.strategies import field_strat

    @field_strat(EnumField)
    @field_strat(IntEnumField)
    @field_strat(StringEnumField)
    def my_custom_strat(field):
        return strategies.sampled_from(field.enum)
