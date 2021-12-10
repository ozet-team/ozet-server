# -*- coding: utf-8 -*-
import copy

from rest_framework import serializers


class SimpleSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.flatten = kwargs.pop('flatten', False)
        super(ModelSerializer, self).__init__(*args, **kwargs)

    def get_fields(self):
        fields = super(ModelSerializer, self).get_fields()
        fields_for_iter = copy.deepcopy(fields)
        for field_name, field in fields_for_iter.items():
            flatten = getattr(field, 'flatten', False)
            if not flatten:
                continue
            del fields[field_name]
            for nested_field_name, nested_field in field.fields.items():
                nested_field.source = (field_name + '.' +
                                       (nested_field.source or nested_field_name))
                fields[nested_field_name] = nested_field
        return fields
