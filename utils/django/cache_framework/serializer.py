# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

from django.core.serializers import register_serializer, base
from django.core.serializers.base import DeserializationError
from django.core.serializers.json import Serializer as JSONSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer


class Serializer(JSONSerializer):

    def start_object(self, obj):
        super(Serializer, self).start_object(obj)
        # noinspection PyAttributeOutsideInit
        self._cf_prefetch_fields = OrderedDict()

    def end_object(self, obj):
        # noinspection PyProtectedMember
        meta = obj._meta
        fk_fields = {f.name: f for f in meta.local_fields if f.remote_field}
        m2m_fields = {f.name: f for f in meta.local_many_to_many}

        for field_name, prefetch in meta.local_cf_prefetch_fields.items():
            prefetch_through = prefetch.prefetch_through
            fk_field = fk_fields.get(prefetch_through)
            m2m_field = m2m_fields.get(prefetch_through)
            self.handle_cf_prefetch_field(obj, field_name, prefetch, fk_field, m2m_field)
        super(Serializer, self).end_object(obj)
        # noinspection PyAttributeOutsideInit
        self._cf_prefetch_fields = None

    def get_dump_object(self, obj):
        data = super(Serializer, self).get_dump_object(obj)
        data['prefetch_fields'] = self._cf_prefetch_fields
        return data

    def handle_m2m_field(self, obj, field):
        # noinspection PyProtectedMember
        if not field.remote_field.through._meta.auto_created:
            return
        qs = getattr(obj, field.name).all()
        if self.use_natural_foreign_keys and hasattr(field.remote_field.model, 'natural_key'):
            def m2m_value(value):
                return value.natural_key()

            self._current[field.name] = [
                m2m_value(related) for related in qs.iterator()
            ]
        else:
            self._current[field.name] = list(qs.values_list(field.target_field.attname, flat=True).all())

    def handle_cf_prefetch_field(self, obj, field_name, prefetch, fk_field, m2m_field):
        if fk_field:
            fk_model = fk_field.remote_field.model
            if self.use_natural_foreign_keys and hasattr(fk_model, 'natural_key'):
                # TODO: support natural_key
                return
            value = self._value_from_field(obj, fk_field)
            # noinspection PyProtectedMember
            pk_field = fk_model._meta.pk.name
            value = prefetch.queryset.filter(**{pk_field: value}).values_list(pk_field, flat=True).first()
            self._cf_prefetch_fields[field_name] = value
        elif m2m_field:
            # noinspection PyProtectedMember
            if not m2m_field.remote_field.through._meta.auto_created:
                return

            qs = getattr(obj, m2m_field.name, None).all() & prefetch.queryset
            if self.use_natural_foreign_keys and hasattr(m2m_field.remote_field.model, 'natural_key'):
                def m2m_value(m2m_obj):
                    return m2m_obj.natural_key()
                self._cf_prefetch_fields[field_name] = [
                    m2m_value(related) for related in qs.iterator()
                ]
            else:
                pk_name = m2m_field.target_field.attname
                self._cf_prefetch_fields[field_name] = list(qs.values_list(pk_name, flat=True).all())


class DeserializedObject(base.DeserializedObject):

    def __init__(self, obj, m2m_data=None, prefetch_data=None):
        super(DeserializedObject, self).__init__(obj, m2m_data=m2m_data)
        self.prefetch_data = prefetch_data


# noinspection PyPep8Naming
def Deserializer(stream_or_string, ignorenonexistent=True, **options):
    """Deserialize a stream or string of JSON data."""
    if not isinstance(stream_or_string, (bytes, str)):
        stream_or_string = stream_or_string.read()
    if isinstance(stream_or_string, bytes):
        stream_or_string = stream_or_string.decode()
    try:
        objects = json.loads(stream_or_string)
        prefetch_fields_data = [o.pop('prefetch_fields', {}) for o in objects]
        for i, deserialized_object in enumerate(PythonDeserializer(objects,
                                                                   ignorenonexistent=ignorenonexistent,
                                                                   **options)):
            prefetch_fields = prefetch_fields_data[i]
            yield DeserializedObject(obj=deserialized_object.object,
                                     m2m_data=deserialized_object.m2m_data,
                                     prefetch_data=prefetch_fields)
    except (GeneratorExit, DeserializationError):
        raise
    except Exception as exc:
        raise DeserializationError() from exc


register_serializer('cache_framework', __name__)
