import bson
import hypothesis.strategies as strat
import mongoengine


field_strats = {}


def register_field(field_class, strategy):
    field_strats[field_class] = strategy


def field_strat(field_class):
    def wrapper(f):
        register_field(field_class, f)
        return f
    return wrapper


@field_strat(mongoengine.ObjectIdField)
def objectid_strat(field):
    return strat.builds(bson.ObjectId)


@field_strat(mongoengine.StringField)
def string_strat(field):
    if field.regex:
        return strat.from_regex(field.regex)
    return strat.text(min_size=field.min_length, max_size=field.max_length)


@field_strat(mongoengine.EmbeddedDocumentListField)
@field_strat(mongoengine.SortedListField)
@field_strat(mongoengine.ListField)
def list_strat(field):
    return strat.lists(_inner_field_values(field.field))


@field_strat(mongoengine.IntField)
def int_strat(field):
    if field.min_value is None:
        min_value = -(2 ** 31)
    else:
        min_value = field.min_value

    if field.max_value is None:
        max_value = 2 ** 31 - 1
    else:
        max_value = field.max_value

    return strat.integers(min_value=min_value, max_value=max_value)


@field_strat(mongoengine.LongField)
def long_strat(field):
    if field.min_value is None:
        min_value = -(2 ** 63)
    else:
        min_value = field.min_value

    if field.max_value is None:
        max_value = 2 ** 63 - 1
    else:
        max_value = field.max_value

    return strat.integers(min_value=min_value, max_value=max_value)


@field_strat(mongoengine.FloatField)
def float_strat(field):
    return strat.floats(min_value=field.min_value, max_value=field.max_value)


@field_strat(mongoengine.BooleanField)
def boolean_strat(field):
    return strat.booleans()


@field_strat(mongoengine.DateTimeField)
def datetime_strat(field):
    # MongoDB datetimes have only millisecond precision
    return strat.datetimes().map(
        lambda dt: dt.replace(microsecond=(dt.microsecond // 1000 * 1000)))


@field_strat(mongoengine.EmbeddedDocumentField)
def embedded_document_strat(field):
    return documents(field.document_type)


@field_strat(mongoengine.BinaryField)
def binary_strat(field):
    return strat.builds(bson.Binary, strat.binary(max_size=field.max_bytes))


@field_strat(mongoengine.ComplexDateTimeField)
def complex_datetime_strat(field):
    return strat.datetimes()


def _inner_field_values(field):
    if field.choices is not None:
        return strat.sampled_from(field.choices)
    else:
        return field_strats[field.__class__](field)


def field_values(field):
    if field.required:
        return _inner_field_values(field)
    else:
        return strat.one_of(strat.none(), _inner_field_values(field))


def documents(doc_class, **kwargs):
    return strat.builds(doc_class, **{k: kwargs.get(k, field_values(v))
                                      for k, v in doc_class._fields.items()})
