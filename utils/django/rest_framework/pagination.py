# -*- coding: utf-8 -*-
from collections import OrderedDict

import coreapi
import coreschema
from rest_framework import pagination
from rest_framework.response import Response

from utils.django.paginators import Paginator


class BasePagination(pagination.BasePagination):

    def paginate_queryset(self, queryset, request, view=None):
        return super(BasePagination, self).paginate_queryset(queryset, request, view=view)

    def get_paginated_response(self, data):
        return super(BasePagination, self).get_paginated_response(data)

    def to_html(self):
        return super(BasePagination, self).to_html()

    # noinspection PyMethodMayBeStatic
    def get_paginated_response_schema_fields(self, view):
        return []


class PerPagePagination(pagination.PageNumberPagination, BasePagination):
    page_size = 20
    page_size_query_param = 'per_page'
    max_page_size = 100
    django_paginator_class = Paginator

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('per_page', self.get_page_size(self.request)),
            ('has_prev', self.get_previous_link() is not None),
            ('has_next', self.get_next_link() is not None),
            ('total_count', self.page.paginator.count),
            ('items', data)
        ]))

    def get_paginated_response_schema_fields(self, view):
        fields = [
            coreapi.Field(
                name='page',
                schema=coreschema.Integer()
            ),
            coreapi.Field(
                name='pages',
                schema=coreschema.Integer()
            ),
            coreapi.Field(
                name='per_page',
                schema=coreschema.Integer()
            ),
            coreapi.Field(
                name='has_prev',
                schema=coreschema.Boolean()
            ),
            coreapi.Field(
                name='has_next',
                schema=coreschema.Boolean()
            ),
            coreapi.Field(
                name='total_count',
                schema=coreschema.Integer()
            ),
            coreapi.Field(
                name='items',
                schema='response_schema'
            ),
        ]
        return fields
