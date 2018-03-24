import bson
import mongoengine.errors
import mongoengine.signals


def mark_saved(doc, validate=True, clean=True, signal_kwargs=None, **kwargs):
    """Simulate mongoengine.Document.save()

    This attempts to do everything that happens during
    :meth:`mongoengine.Document.save` except actually talking to a database.

    """
    if doc._meta.get('abstract'):
        raise mongoengine.errors.InvalidDocumentError(
            'Cannot save an abstract document.')

    signal_kwargs = signal_kwargs or {}
    mongoengine.signals.pre_save.send(
        doc.__class__, document=doc, **signal_kwargs)

    if validate:
        doc.validate(clean=clean)

    created = doc.pk is None or doc._created

    mongoengine.signals.pre_save_post_validation.send(
        doc.__class__, document=doc, created=created, **signal_kwargs)

    if doc.pk is None:
        doc.pk = bson.ObjectId()

    mongoengine.signals.post_save.send(
        doc.__class__, document=doc, created=created, **signal_kwargs)

    doc._clear_changed_fields()
    doc._created = False

    return doc
