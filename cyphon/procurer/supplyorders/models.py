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
Defines a |SupplyOrder| model for processing |Procurements| for
|AppUsers|.

============================  ================================================
Class                         Description
============================  ================================================
:class:`~SupplyOrder`         Handles a |Procurement| for an |AppUser|.
:class:`~SupplyOrderManager`  Model manager for |SupplyOrders|.
============================  ================================================

"""

# standard library
import logging

# third party
from django.conf import settings
from django.contrib.postgres.fields.jsonb import JSONField
from django.db import models
from django.utils import timezone
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
        """Get |SupplyOrders| accessible by a given user.

        Returns
        -------
        |Queryset|
            A |Queryset| of |SupplyOrders| accessible by a given user.

        """
        if queryset is not None:
            supplyorder_qs = queryset
        else:
            supplyorder_qs = self.get_queryset()

        if not user.is_staff:
            return supplyorder_qs.filter(user=user)
        else:
            return supplyorder_qs


class SupplyOrder(models.Model):
    """Processes a |Procurement| for an |AppUser|.

    Attributes
    ----------
    procurement : Procurement
        The |Procurement| used to process the |SupplyOrder|.

    user : AppUser
        The |AppUser| associated with the |SupplyOrder|.

    alert : Alert
        The |Alert| associated with the |SupplyOrder|.

    input_data : dict
        The data used as the input for the |SupplyChain|.

    distillery : Distillery
        The |Distillery| in which the |SupplyOrder|'s result is saved.

    doc_id : str
        The document id of the saved result.

    created_date : datetime
        A |datetime| for when the |SupplyOrder| was created.

    """

    procurement = models.ForeignKey(
        Procurement,
        related_name='supply_orders',
        related_query_name='supply_order',
        verbose_name=_('procurement'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        verbose_name=_('user'),
    )
    alert = models.ForeignKey(
        Alert,
        related_name='supply_orders',
        related_query_name='supply_order',
        verbose_name=_('alert'),
        blank=True,
        null=True,
    )
    input_data = JSONField(
        default=dict,
        verbose_name=_('input data'),
        help_text=_('The data used to make the request.')
    )
    distillery = models.ForeignKey(
        Distillery,
        blank=True,
        null=True,
        verbose_name=_('distillery'),
        db_index=True,
        on_delete=models.PROTECT,
        help_text=_('The Distillery where the results are saved.')
    )
    doc_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('document id'),
        db_index=True,
        help_text=_('The id of the document containing the results.')
    )
    created_date = models.DateTimeField(default=timezone.now, db_index=True)

    objects = SupplyOrderManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supply order')
        verbose_name_plural = _('supply orders')
        ordering = ['-id']

    def __str__(self):
        """A string representation of a SupplyOrder."""
        return '%s %s' % (self.__class__.__name__, self.pk)

    @property
    def result(self):
        """A |dict| of results associated with the |SupplyOrder|.

        Returns a |dict| of the document for the |SupplyOrder| if it can
        be found. If not, returns an empty |dict|.
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
        """A |dict| of input field names mapped to their data types.

        Returns a dictionary in which keys are the names of input fields
        and the values are the field types.
        """
        return self.procurement.input_fields

    def associate_alert(self, alert):
        """Associate an |Alert| with the |SupplyOrder|.

        Parameters
        ----------
        alert : |Alert|
            The |Alert| to associate with eth |SupplyOrder|.

        Returns
        -------
        self

        """
        self.alert = alert
        self.save()
        return self

    def update_result(self, distillery, doc_id):
        """Update the |SupplyOrder| with the storage location of its result.

        Parameters
        ----------
        distillery : |Distillery|
            The |Distillery| where the |SupplyOrder|'s result is saved.

        doc_id : dict
            The document id for the |SupplyOrder|'s result.

        Returns
        -------
        self

        """
        self.distillery = distillery
        self.doc_id = doc_id
        self.save()
        return self

    def use_alert_data(self):
        """Use date from the |SupplyOrder|'s |Alert| for the input data.

        Returns
        -------
        self

        """
        input_data = {}
        alert_data = self.alert.data
        for key, dummy_val in self.input_fields.items():
            input_data[key] = alert_data.get(key)
        self.input_data = input_data
        self.save()
        return self

    def process(self):
        """Process and update a |SupplyOrder|.

        Parameters
        ----------
        supply_order : |SupplyOrder|
            The |SupplyOrder| that will process and save the data.

        Returns
        -------
            The processed and updated |SupplyOrder|.

        """
        return self.procurement.process(self)
