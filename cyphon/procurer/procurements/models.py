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
from procurer.supplychains.models import SupplyChain
from sifter.datasifter.datamungers.models import DataMunger

_LOGGER = logging.getLogger(__name__)


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
