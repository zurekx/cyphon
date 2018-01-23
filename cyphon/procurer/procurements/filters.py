# -*- coding: utf-8 -*-
# Copyright 2017 Dunbar Security Solutions, Inc.
#
# This file is part of Cyphon Engine.
#
# Cyphon Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Cyphon Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
"""
Defines filters for Procurements.
"""

# third party
from django_filters.rest_framework import DjangoFilterBackend

# local
from .models import Procurement


class ProcurementFilterBackend(DjangoFilterBackend):
    """
    Provides a filter backend to only show |Procurements| for which the
    current user has an available |Quartermaster| and access to the
    |Procurement|'s |DataMunger|.
    """

    def filter_queryset(self, request, queryset, view):
        """Return a filtered queryset.

        Implements `custom filtering`_.

        Parameters
        ----------
        request : Request
             A `Request`_ for a resource.

        queryset : QuerySet
            A |QuerySet| to be filtered.

        view : ModelViewSet
            A `ModelViewSet`_

        Returns
        -------
        QuerySet
            A |QuerySet| filtered to only show |Procurements| for which the
            current user has access.

        """
        return Procurement.objects.filter_by_user(request.user, queryset)
