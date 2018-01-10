# -*- coding: utf-8 -*-
# Copyright 2017-2018 Dunbar Security Solutions, Inc.
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
Defines filters for Endpoints.
"""

# third party
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend


class EndpointFilterBackend(DjangoFilterBackend):
    """
    Provides a filter backend to only show |Endpoints| for which the
    current user has an available |Emissary|.

    """

    def filter_queryset(self, request, queryset, view):
        """Return a filtered queryset.

        Implements `custom filtering`_.

        Parameters
        ----------
        request : Request
             A |Request| for a resource.

        queryset : QuerySet
            A |QuerySet| to be filtered.

        view : ModelViewSet
            A |ModelViewSet|.

        Returns
        -------
        QuerySet
            A |QuerySet| filtered to only show |Endpoints| for which the
            current user has an available |Emissary|.

        """
        has_user = Q(emissary__passport__users=request.user)
        is_public = Q(emissary__passport__public=True)

        return queryset.filter(has_user | is_public).distinct()
