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
from django.utils.translation import ugettext_lazy as _

# local
# from bottler.containers.models import Container
from trader.requisition.models import Requisition
from sifter.datasifter.datacondensers.models import DataCondenser
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

    def start(self, data):
        """

        """
        pass


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

        verbose_name = _('supply link')
        verbose_name_plural = _('supply links')
