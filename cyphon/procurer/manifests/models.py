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
Defines a model for recording the results of an API request returned by
a |Convoy|.

===========================  ================================================
Class                        Description
===========================  ================================================
:class:`~Manifest`           Records the results of an API request.
===========================  ================================================

"""

# third party
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.records.models import Record, RecordManager
from procurer.supplyorders.models import SupplyOrder


class Manifest(Record):
    """Provides a record of an API call.

    Attributes
    ----------
    stamp : Stamp
        A |Stamp| recording the details of the API call.

    supply_order : SupplyOrder
        A |SupplyOrder| associated with the Manifest.

    data : dict
        A dictionary containing the response to the API request.

    """

    supply_order = models.ForeignKey(
        SupplyOrder,
        related_name='manifests',
        related_query_name='manifest',
        verbose_name=_('supply order'),
        blank=True,
        null=True
    )
    data = JSONField(blank=True, null=True, verbose_name=_('data'))

    objects = RecordManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('Manifest')
        verbose_name_plural = _('manifests')
