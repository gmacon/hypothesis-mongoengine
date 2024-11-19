import datetime
import uuid

import bson
import hypothesis.strategies as st
import mongoengine

from .geojson import line_strings, points, polygons


field_strategies = {}


def register_field(field_class, strategy):
    field_strategies[field_class] = strategy


def field_strategy(field_class):
    def wrapper(f):
        register_field(field_class, f)
        return f

    return wrapper


@field_strategy(mongoengine.ObjectIdField)
def objectid_strat(field):
    return st.builds(bson.ObjectId)


@field_strategy(mongoengine.StringField)
def string_strat(field):
    if field.regex:
        return st.from_regex(field.regex)
    return st.text(min_size=field.min_length or 0, max_size=field.max_length)


@field_strategy(mongoengine.EmbeddedDocumentListField)
@field_strategy(mongoengine.SortedListField)
@field_strategy(mongoengine.ListField)
def list_strat(field):
    return st.lists(_inner_field_values(field.field))


@field_strategy(mongoengine.IntField)
def int_strat(field):
    if field.min_value is None:
        min_value = -(2**31)
    else:
        min_value = field.min_value

    if field.max_value is None:
        max_value = 2**31 - 1
    else:
        max_value = field.max_value

    return st.integers(min_value=min_value, max_value=max_value)


@field_strategy(mongoengine.LongField)
def long_strat(field):
    if field.min_value is None:
        min_value = -(2**63)
    else:
        min_value = field.min_value

    if field.max_value is None:
        max_value = 2**63 - 1
    else:
        max_value = field.max_value

    return st.integers(min_value=min_value, max_value=max_value)


@field_strategy(mongoengine.FloatField)
def float_strat(field):
    return st.floats(min_value=field.min_value, max_value=field.max_value)


@field_strategy(mongoengine.BooleanField)
def boolean_strat(field):
    return st.booleans()


@field_strategy(mongoengine.DateTimeField)
def datetime_strat(field):
    # MongoDB datetimes have only millisecond precision
    return st.datetimes().map(
        lambda dt: dt.replace(microsecond=(dt.microsecond // 1000 * 1000))
    )


@field_strategy(mongoengine.EmbeddedDocumentField)
def embedded_document_strat(field):
    return documents(field.document_type)


@field_strategy(mongoengine.BinaryField)
def binary_strat(field):
    return st.builds(bson.Binary, st.binary(max_size=field.max_bytes))


@field_strategy(mongoengine.ComplexDateTimeField)
def complex_datetime_strat(field):
    return st.datetimes(min_value=datetime.datetime(1900, 1, 1))


def mongodb_keys():
    return st.text(
        st.characters(blacklist_characters="\0.$", blacklist_categories=["Cs"])
    )


@field_strategy(mongoengine.MapField)
def map_strat(field):
    return st.dictionaries(keys=mongodb_keys(), values=_inner_field_values(field.field))


@field_strategy(mongoengine.UUIDField)
def uuid_strat(field):
    return st.builds(uuid.uuid4)


@field_strategy(mongoengine.GeoPointField)
def geo_point_strat(field):
    return points()


@field_strategy(mongoengine.PointField)
def point_strat(field):
    return points()


@field_strategy(mongoengine.LineStringField)
def line_string_strat(field):
    return line_strings()


@field_strategy(mongoengine.PolygonField)
def polygon_strat(field):
    return polygons()


@field_strategy(mongoengine.MultiPointField)
def multi_point_strat(field):
    return st.lists(points(), min_size=1)


@field_strategy(mongoengine.MultiLineStringField)
def multi_line_string_strat(field):
    return st.lists(line_strings(), min_size=1)


@field_strategy(mongoengine.MultiPolygonField)
def multi_polygon_strat(field):
    return st.lists(polygons(), min_size=1)


def validation_adapter(validator):
    def adapted(value):
        try:
            rv = validator(value)
        except mongoengine.ValidationError:
            return False
        if rv is None:
            return True
        return rv

    return adapted


def _inner_field_values(field):
    if field.choices is not None:
        values = st.sampled_from(field.choices)
    else:
        values = field_strategies[field.__class__](field)
    if field.validation is not None:
        values = values.filter(validation_adapter(field.validation))
    return values


def field_values(field, *, required=None):
    if required is None:
        required = field.required
    if required:
        return _inner_field_values(field)
    else:
        return st.one_of(st.none(), _inner_field_values(field))


def documents(doc_class, **kwargs):
    builds_kwargs = {}
    for k, v in doc_class._fields.items():
        if k in kwargs:
            builds_kwargs[k] = kwargs[k]
        else:
            builds_kwargs[k] = field_values(v)
    return st.builds(doc_class, **builds_kwargs)
