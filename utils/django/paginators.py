# -*- coding: utf-8 -*-
from django.core.paginator import Paginator as BasePaginator, EmptyPage, PageNotAnInteger
from django.utils.translation import ugettext


class Paginator(BasePaginator):

    def validate_number(self, number):
        """Validate the given 1-based page number."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger(ugettext('That page number is not an integer'))
        if number < 1:
            raise EmptyPage(ugettext('That page number is less than 1'))
        return number
