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
Serializers for SupplyOrders.
"""

# third party
from rest_framework import serializers

# local
from procurer.manifests.serializers import ManifestSerializer
from .models import SupplyOrder


class SupplyOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for SupplyOrders.
    """

    manifests = ManifestSerializer(many=True)

    class Meta(object):
        """Metadata options."""

        model = SupplyOrder
        fields = (
            'id',
            'created_date',
            'procurement',
            'alert',
            'user',
            'input_data',
            'distillery',
            'doc_id',
            'results',
            'manifests'
        )
