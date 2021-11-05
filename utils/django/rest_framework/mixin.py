# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

import coreapi
import coreschema
from django.conf import settings
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django_replicated.decorators import use_slave
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .pagination import BasePagination


class ClientIPContextMixin(APIView):

    @cached_property
    def client_ip(self):
        if not hasattr(self, 'request') or not self.request:
            return None
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def initialize_request(self, request, *args, **kwargs):
        request = super(ClientIPContextMixin, self).initialize_request(request, *args, **kwargs)
        request.client_ip = self.client_ip
        return request

    def get_serializer_context(self):
        if not hasattr(super(ClientIPContextMixin, self), 'get_serializer_context'):
            return

        # noinspection PyUnresolvedReferences
        context = super(ClientIPContextMixin, self).get_serializer_context()
        if isinstance(self.request, Request):
            context['client_ip'] = self.client_ip
        return context


class ClientVersionContextMixin(APIView):

    @cached_property
    def client_os(self):
        if not hasattr(self, 'request') or not self.request:
            return None
        version = self.request.META.get('HTTP_X_CHATIE_VERSION', '')
        index = version.find('/')
        os, version = version[:index], version[index + 1:]
        return os

    @cached_property
    def client_app_version(self):
        if not hasattr(self, 'request') or not self.request:
            return None
        version = self.request.META.get('HTTP_X_CHATIE_VERSION', '')
        index = version.find('/')
        os, version = version[:index], version[index + 1:]
        return version

    def initialize_request(self, request, *args, **kwargs):
        request = super(ClientVersionContextMixin, self).initialize_request(request, *args, **kwargs)
        request.client_os = self.client_os
        request.client_app_version = self.client_app_version
        return request

    def get_serializer_context(self):
        if not hasattr(super(ClientVersionContextMixin, self), 'get_serializer_context'):
            return

        # noinspection PyUnresolvedReferences
        context = super(ClientVersionContextMixin, self).get_serializer_context()
        if isinstance(self.request, Request):
            context['client_os'] = self.client_os
            context['client_app_version'] = self.client_app_version
        return context


class UserContextMixin(APIView):

    @cached_property
    def user(self):
        if getattr(self, 'swagger_fake_view', False):
            return None

        if hasattr(self.request, 'user'):
            user = self.request.user
            if user.is_authenticated:
                return user
        return None

    def get_serializer_context(self):
        if not hasattr(super(UserContextMixin, self), 'get_serializer_context'):
            return

        # noinspection PyUnresolvedReferences
        context = super(UserContextMixin, self).get_serializer_context()
        if isinstance(self.request, Request):
            context['user'] = self.user
        return context


class ReplicaDatabaseMixin(APIView):
    use_replica_db = True

    def dispatch(self, request, *args, **kwargs):
        view_func = super(ReplicaDatabaseMixin, self).dispatch
        testing = getattr(settings, 'PY_TEST', False)
        if self.use_replica_db and request.method.upper() in SAFE_METHODS and not testing:
            return use_slave(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)


class Create200Mixin(object):
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)


class PersonalizedListMixin(GenericAPIView):

    # noinspection PyMethodMayBeStatic
    def get_personalized_list(self, iterator):
        return iterator

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            page = self.get_personalized_list(page)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        queryset = self.get_personalized_list(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SimpleItemListMixin(PersonalizedListMixin):

    class Pagination(BasePagination):
        def get_schema_fields(self, view):
            fields = []
            if view.page_size:
                fields.append(
                    coreapi.Field(
                        name=view.last_evaluated_key_query_param,
                        required=False,
                        location='query',
                        schema=coreschema.String(
                            title=view.last_evaluated_key_query_param,
                            description=force_text(view.last_evaluated_key_query_description)
                        )
                    )
                )
            return fields

        def get_paginated_response_schema_fields(self, view):
            fields = [
                coreapi.Field(
                    name='last_evaluated_key',
                    schema=coreschema.String()
                ),
                coreapi.Field(
                    name='items',
                    schema='response_schema'
                ),
            ]
            return fields

    page_size = api_settings.PAGE_SIZE

    last_evaluated_key_query_param = 'last_evaluated_key'
    last_evaluated_key_query_description = 'LastEvaluatedKey'

    pagination_class = Pagination

    filter_backends = []

    max_loop = None

    def get_last_evaluated_key(self, request):
        if not self.page_size or not self.last_evaluated_key_query_param:
            return None
        return self.decode_last_evaluated_key(request.query_params.get(self.last_evaluated_key_query_param, None))

    # noinspection PyMethodMayBeStatic
    def encode_last_evaluated_key(self, last_evaluated_key):
        if not last_evaluated_key:
            return None
        return str(last_evaluated_key)

    # noinspection PyMethodMayBeStatic
    def decode_last_evaluated_key(self, last_evaluated_key):
        if not last_evaluated_key:
            return None
        try:
            return int(last_evaluated_key)
        except (TypeError, ValueError):
            pass
        return None

    def get_items(self):  # pragma: no cover
        raise NotImplementedError('get_items() must be implemented.')

    # noinspection PyMethodMayBeStatic
    def get_filtered_items(self, items):
        return items

    # noinspection PyMethodMayBeStatic
    def get_page(self, items, page_size, last_evaluated_key=None):
        if not page_size:
            return items, None

        if not last_evaluated_key:
            page_items = items[:page_size]
            last_evaluated_key = page_size - 1 if len(items) > page_size else None
            return page_items, last_evaluated_key

        next_index = last_evaluated_key + 1
        last_index = next_index + page_size
        page_items = items[next_index:last_index]
        last_evaluated_key = last_index - 1 if len(items) > last_index else None
        return page_items, last_evaluated_key

    # noinspection PyMethodMayBeStatic
    def get_filtered_page_items(self, page_items):
        return page_items

    def list(self, request, *args, **kwargs):
        items = self.get_filtered_items(self.get_items())

        if not self.page_size:
            return items

        page_size = self.page_size
        last_evaluated_key = self.get_last_evaluated_key(request)
        filtered_page_items = []
        loop = 0
        while True:
            page_items, last_evaluated_key = self.get_page(items,
                                                           page_size=page_size,
                                                           last_evaluated_key=last_evaluated_key)
            filtered_page_items += self.get_filtered_page_items(page_items)
            filtered_page_item_count = len(filtered_page_items)
            if not last_evaluated_key or filtered_page_item_count >= self.page_size:
                break

            page_size = self.page_size - filtered_page_item_count

            loop += 1
            if self.max_loop and loop >= self.max_loop:
                break
        filtered_page_items = self.get_personalized_list(filtered_page_items)
        serializer = self.get_serializer(filtered_page_items, many=True)
        return Response(OrderedDict([
            ('last_evaluated_key', self.encode_last_evaluated_key(last_evaluated_key)),
            ('items', serializer.data)
        ]))


class DDBListMixin(PersonalizedListMixin, GenericAPIView):
    use_ddb = True

    page_size = api_settings.PAGE_SIZE

    pagination_class = None

    last_evaluated_key_query_param = 'key'

    ddb_scan_index_forward = False

    def get_queryset(self):
        return None

    def get_queryable(self, request):
        """

        :example:
            def get_queryable(self):
                return TestModel

            def get_queryable(self):
                return TestModel.test_gix
        """
        raise NotImplementedError('get_queryable() must be implemented.')

    def get_query_params(self, request):
        raise NotImplementedError('get_query_params() must be implemented.')

    def get_last_evaluated_key(self, request):
        if self.last_evaluated_key_query_param:
            # noinspection PyBroadException
            try:
                return json.loads(request.query_params[self.last_evaluated_key_query_param])
            except Exception:
                pass
        return None

    # noinspection PyMethodMayBeStatic
    def get_filtered_items(self, items):
        return items

    def get_query_result(self, request, last_evaluated_key, page_size=None):
        queryable = self.get_queryable(request)
        query_params = self.get_query_params(request)

        # limit
        if not page_size:
            page_size = self.page_size
        query_params['limit'] = page_size + 1

        # last_evaluated_key
        if last_evaluated_key:
            query_params['last_evaluated_key'] = last_evaluated_key

        # scan_index_forward
        query_params['scan_index_forward'] = self.ddb_scan_index_forward

        result_iter = queryable.query(**query_params)
        items = list(result_iter)
        if not items:
            return [], None

        has_next = len(items) > page_size
        last_evaluated_key = None
        if has_next:
            # noinspection PyProtectedMember
            result_iter._index -= 1
            items = items[:page_size]
            last_evaluated_key = result_iter.last_evaluated_key

        filtered_items = self.get_filtered_items(items)
        filtered_item_count = len(filtered_items)
        if not has_next or filtered_item_count >= page_size:
            return filtered_items, last_evaluated_key

        next_items, last_evaluated_key = self.get_query_result(request,
                                                               last_evaluated_key=last_evaluated_key,
                                                               page_size=page_size - filtered_item_count)
        filtered_items += next_items
        return filtered_items, last_evaluated_key

    def list(self, request, *args, **kwargs):
        last_evaluated_key = self.get_last_evaluated_key(request)
        items, last_evaluated_key = self.get_query_result(request, last_evaluated_key)
        items = self.get_personalized_list(items)
        has_next = last_evaluated_key is not None
        serializer = self.get_serializer(items, many=True)
        return Response(OrderedDict([
            ('has_next', has_next),
            ('next_key', json.dumps(last_evaluated_key) if last_evaluated_key else None),
            ('items', serializer.data)
        ]))

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class QuerySerializerMixin(object):

    query_serializer_class = None

    def get_query_serializer_class(self):
        assert self.query_serializer_class is not None, (
            "'%s' should either include a `query_serializer_class` attribute, "
            "or override the `get_query_serializer_class()` method."
            % self.__class__.__name__
        )

        return self.query_serializer_class

    def get_query_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_query_serializer(self, *args, **kwargs):
        serializer_class = self.get_query_serializer_class()
        kwargs['context'] = self.get_query_serializer_context()
        return serializer_class(*args, **kwargs)

    def validate_query_params(self):
        serializer = self.get_query_serializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data
