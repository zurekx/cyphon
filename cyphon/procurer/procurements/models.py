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
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from cyphon.documents import DocumentObj
from cyphon.models import GetByNameManager
from distilleries.models import Distillery
from procurer.supplychains.models import SupplyChain
from sifter.datasifter.datamungers.models import DataMunger

_LOGGER = logging.getLogger(__name__)


class ProcurementManager(GetByNameManager):
    """Manage |Procurement| objects.

    Adds methods to the default Django model manager.
    """

    def filter_by_user(self, user, queryset=None):
        """Get |Procurements| that can be executed by the given user.

        Returns
        -------
        |Queryset|
            A |Queryset| of |Procurements| can be executed by the given
            user.

        """
        if queryset is not None:
            procurement_qs = queryset
        else:
            procurement_qs = self.get_queryset()

        supplychains = SupplyChain.objects.filter_by_user(user)
        distilleries = Distillery.objects.filter_by_user(user)
        return procurement_qs.filter(supply_chain__in=supplychains,
                                     munger__distillery__in=distilleries)


class Procurement(models.Model):
    """

    Attributes
    ----------
    name : str

    supply_chain : SupplyChain
        The |SupplyChain| that will procure the data.

    munger : DataMunger
        The |DataMunger| that will process and save the data.

    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('name')
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        related_name='procurements',
        related_query_name='procurement',
        verbose_name=_('supply chain')
    )
    munger = models.ForeignKey(
        DataMunger,
        related_name='procurements',
        related_query_name='procurement',
        verbose_name=_('data munger')
    )

    class Meta(object):
        """Metadata options."""

        ordering = ['name']
        unique_together = ['supply_chain', 'munger']

    @property
    def input_fields(self):
        """
        Returns a dictionary in which keys are the names of input fields
        and the values are the field types.
        """
        return self.supply_chain.input_fields

    def _get_result(self, suppy_order):
        """Return the result of a Procurement request.

        Takes a dictionary of data and an AppUser, and submits them as a
        SupplyChain request. If the request is succesful, returns a
        data dictionary of the result. Otherwise, returns None.
        """
        return self.supply_chain.start(suppy_order)

    def _get_platform_name(self):
        """Return the name of the Platform associated with the Procurement."""
        return str(self.supply_chain.platform)

    def _get_doc_obj(self, result):
        """Return a DocumentObj for a result."""
        platform = self._get_platform_name()
        return DocumentObj(data=result, platform=platform)

    def _process_doc(self, doc_obj):
        """Parse and save data from a DocumentObj."""
        return self.munger.process(doc_obj)

    def validate(self, data):
        """

        """
        pass

    def process(self, suppy_order):
        """

        Attributes
        ----------
        data : dict

        user : AppUser
            The |SupplyChain| that will procure the data.

        munger : DataMunger
            The |DataMunger| that will process and save the data.

        """
        result = self._get_result(suppy_order)
        if result:
            doc_obj = self._get_doc_obj(result)
            return self._process_doc(doc_obj)
