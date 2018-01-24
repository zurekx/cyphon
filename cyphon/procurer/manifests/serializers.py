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
Defines a serializer for |Manifests|.

====================================  ========================================
Class                                 Description
====================================  ========================================
:class:`~ManifestSerializer`          Serializer for |Manifest| views.
====================================  ========================================

"""

# third party
from rest_framework import serializers

# local
from appusers.serializers import AppUserSerializer
from .models import Manifest


class ManifestSerializer(serializers.ModelSerializer):
    """Serializer for |Manifests|."""

    issued_by = AppUserSerializer()

    class Meta(object):
        """Metadata options."""

        model = Manifest
        fields = (
            'id',
            'supply_order',
            'issued_by',
            'status_code',
            'response_msg',
            'data',
        )
