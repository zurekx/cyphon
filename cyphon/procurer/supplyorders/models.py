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

# standard library
import logging

# third party
from django.conf import settings
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from alerts.models import Alert
from distilleries.models import Distillery
from procurer.procurements.models import Procurement

_LOGGER = logging.getLogger(__name__)


class SupplyOrderManager(models.Manager):
    """Manage |SupplyOrder| objects.

    Adds methods to the default Django model manager.
    """

    def filter_by_user(self, user, queryset=None):
        """Get |SupplyOrders| that can be executed by the given user.

        Returns
        -------
        |Queryset|
            A |Queryset| of |SupplyOrders| can be executed by the given
            user.

        """
        if queryset is not None:
            supplyorder_qs = queryset
        else:
            supplyorder_qs = self.get_queryset()

        procurements = Procurement.objects.filter_by_user(user)
        return supplyorder_qs.filter(procurement__in=procurements)


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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        verbose_name=_('user'),
    )
    input_data = JSONField(default=dict, verbose_name=_('input data'))
    distillery = models.ForeignKey(
        Distillery,
        blank=True,
        null=True,
        verbose_name=_('distillery'),
        db_index=True,
        on_delete=models.PROTECT
    )
    doc_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('document id'),
        db_index=True,
    )

    objects = SupplyOrderManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supply order')
        verbose_name_plural = _('supply orders')

    @property
    def results(self):
        """
        Returns the document for the SupplyOrder if it can be found.
        If not, returns an empty dictionary.
        """
        if self.distillery and self.doc_id:
            data = self.distillery.find_by_id(self.doc_id)
            if data:
                return data
            else:
                _LOGGER.warning('The document associated with id %s cannot be '
                                'found in %s.', self.doc_id, self.distillery)
        return {}

    @property
    def input_fields(self):
        """
        Returns a dictionary in which keys are the names of input fields
        and the values are the field types.
        """
        return self.procurement.input_fields

    def associate_alert(self, alert):
        """

        """
        self.alert = alert
        self.save()

    def use_alert_data(self):
        """
        Uses values from the Alert data for the SupplyOrder data.
        """
        input_data = {}
        alert_data = self.alert.data
        for key, dummy_val in self.input_fields.items():
            input_data[key] = alert_data.get(key)
        self.input_data = input_data
        self.save()

    def process(self):
        """

        """
        self.doc_id = self.procurement.process(self)
        self.distillery = self.procurement.distillery
        self.save()
        return self
