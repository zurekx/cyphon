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
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# local
# from bottler.containers.models import Container
from procurer.requisition.models import Requisition
from sifter.datasifter.datacondensers.models import DataCondenser
from .exceptions import SupplyChainException
# from cyphon.transaction import close_old_connections
# from sifter.datasifter.datachutes.models import DataChute


class SupplyChain(models.Model):
    """

    Attributes
    ----------
    name : str

    """

    name = models.CharField(max_length=255, verbose_name=_('name'))

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supply chain')
        verbose_name_plural = _('supply chains')

    @cached_property
    def _first_link(self):
        """

        """
        return self.supplylinks.first()

    def _get_transport(self, supply_link):
        """

        """
        pass
        # get Transport for SupplyLink

    def start(self, data):
        """

        """
        input_doc = data
        for link in self.supplylinks.all():
            if link.validate(input_doc):
                input_doc = link.process(input_doc)
        return input_doc


class SupplyLink(models.Model):
    """

    Attributes
    ----------
    chain : SupplyChain
        The |SupplyChain| associated with the SupplyLink.

    requisition : Requisition
        The |Requisition| associated with the SupplyLink.

    condenser : DataCondenser
        The |DataCondenser| used to transform input data into a form the
        `requisition` can use.

    position : int
        An |int| representing the order of the SupplyLink in a
        |SupplyChain|. SupplyLink are evaluated in ascending order (the
        lowest rank first)

    """

    supply_chain = models.ForeignKey(
        SupplyChain,
        related_name='supplylinks',
        related_name_query='supplylink',
        verbose_name=_('supply chain')
    )
    requisition = models.ForeignKey(Requisition, verbose_name=_('requisition'))
    condenser = models.ForeignKey(
        DataCondenser,
        verbose_name=_('data condenser')
    )
    position = models.IntegerField(
        default=0,
        verbose_name=_('position'),
        help_text=_('An integer representing the order of this step in the '
                    'Supply Chain. Steps are performed in ascending order, '
                    'with the lowest number performed first.')
    )

    class Meta(object):
        """Metadata options."""

        order = ['supply_chain', 'position']
        verbose_name = _('supply link')
        verbose_name_plural = _('supply links')

    def _format_request(self, data):
        """

        """
        pass
        # transform input data into request data using condenser

    def _validate(self, data):
        """

        """
        pass

    def get_bottle(self):
        """

        """
        return self.condenser.bottle

    def _create_transport(self):
        """

        """
        pass
        # start Transport

    def process(self, data):
        """

        """
        # create Transport
        is_valid = self._validate(data)
        if is_valid:
            transport = self._create_transport(data)
            return transport.start()
        else:
            # TODO(LH): add error message with identifying info
            raise SupplyChainException()
