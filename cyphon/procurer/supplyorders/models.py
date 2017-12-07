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

"""

# third party
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# local
from alerts.models import Alert
from procurer.procurements.models import Procurement


class SupplyOrder(models.Model):
    """

    Attributes
    ----------
    name : str

    """

    procurement = models.ForeignKey(
        Procurement,
        related_name='supply_orders',
        related_query_name='supply_order',
        verbose_name=_('procurement')
    )
    alert = models.ForeignKey(
        Alert,
        related_name='supply_orders',
        related_query_name='supply_order',
        verbose_name=_('alert'),
        blank=True,
        null=True
    )
    data = JSONField(default=dict)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    # objects = SupplyOrderManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supply order')
        verbose_name_plural = _('supply orders')

    def populate_fields(self):
        """
        Uses values from the Alert data for the SupplyOrder data.
        """
        pass

    def get_input_fields(self):
        """
        Returns a dictionary in which keys are the names of input fields
        and the values are the field types.
        """
        return self.procurement.input_fields

    def process(self):
        """

        """
        return self.procurement.process(self)
