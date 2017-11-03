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
from celery import chain
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# local
# from bottler.containers.models import Container
from cyphon.models import GetByNameManager
from cyphon.celeryapp import app
from cyphon.choices import TIME_UNIT_CHOICES
from procurer.requisitions.models import Requisition, Parameter
from procurer.convoy import Convoy
import utils.dateutils.dateutils as dt
from .exceptions import SupplyChainException
# from cyphon.transaction import close_old_connections
# from sifter.datasifter.datachutes.models import DataChute


@app.task
def start_supplylink(supplylink, data):
    """

    """
    return supplylink.process(data)


class SupplyChain(models.Model):
    """

    Attributes
    ----------
    name : str

    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('name')
    )

    objects = GetByNameManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supply chain')
        verbose_name_plural = _('supply chains')

    def start(self, data):
        """

        """
        return chain(
            start_supplylink.s(supplylink, countdown=supplylink.coutdown)
            for supplylink in self.supplylinks.all()
        )


class SupplyLink(models.Model):
    """

    Attributes
    ----------
    chain : SupplyChain
        The |SupplyChain| associated with the SupplyLink.

    requisition : Requisition
        The |Requisition| associated with the SupplyLink.

    position : int
        An |int| representing the order of the SupplyLink in a
        |SupplyChain|. SupplyLinks are evaluated in ascending order (the
        lowest rank first)

    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('name')
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        related_name='supplylinks',
        related_query_name='supplylink',
        verbose_name=_('supply chain')
    )
    requisition = models.ForeignKey(Requisition, verbose_name=_('requisition'))
    position = models.IntegerField(
        default=0,
        verbose_name=_('position'),
        help_text=_('An integer representing the order of this step in the '
                    'Supply Chain. Steps are performed in ascending order, '
                    'with the lowest number performed first.')
    )
    wait_time = models.IntegerField(verbose_name=_('wait interval'))
    time_unit = models.CharField(
        max_length=3,
        choices=TIME_UNIT_CHOICES,
        verbose_name=_('time unit')
    )

    objects = GetByNameManager()

    class Meta(object):
        """Metadata options."""

        ordering = ['supply_chain', 'position']
        unique_together = ['supply_chain', 'position']
        verbose_name = _('supply link')
        verbose_name_plural = _('supply links')

    @cached_property
    def coupling(self):
        """

        """
        coupling = {}
        for field_coupling in self.field_couplings.all():
            field_coupling.update(field_coupling.mapping)
            return coupling

    @property
    def countdown_seconds(self):
        """
        Returns the number of seconds bedore.
        """
        return dt.convert_time_to_seconds(self.time_interval, self.time_unit)

    def _get_params(self, data):
        """

        """
        params = {}
        for (field_name, param_name) in self.coupling.items():
            params[param_name] = data.get(field_name)
        return params

    def _create_transport(self, user):
        """

        """
        return Convoy(endpoint=self.requisition, user=user)

    def _validate(self, data):
        """

        """
        for coupling in self.couplings.all():
            if not coupling.validate(data):
                # TODO(LH): add message to exception
                raise SupplyChainException()
        return True

    def process(self, user, data):
        """

        Parameters
        ----------
        user : |AppUser|
            The user making the API request.

        data : |dict|
            A dictionary of data used to construct the API request.

        Returns
        -------
        |Convoy|

        Raises
        ------
        SupplyChainException

        """
        self._validate(data)

        params = self._get_params(data)
        transport = self._create_transport(user)
        transport.run(params)

        if transport.cargo:
            return transport.cargo.data
        else:
            # TODO(LH): add message to exception
            raise SupplyChainException()


class FieldCoupling(models.Model):
    """

    Attributes
    ----------
    supply_link : SupplyLink
        The |SupplyLink| associated with the Coupling.

    parameter : Parameter
        The |Parameter| associated with the Coupling.

    """

    supply_link = models.ForeignKey(
        SupplyLink,
        related_name='field_couplings',
        related_query_name='field_coupling',
        verbose_name=_('supply link')
    )
    parameter = models.ForeignKey(
        Parameter,
        related_name='field_couplings',
        related_query_name='field_coupling',
        verbose_name=_('parameter')
    )
    field_name = models.CharField(
        max_length=64,
        verbose_name=_('field name')
    )

    class Meta(object):
        """Metadata options."""

        ordering = ['supply_link', 'parameter']
        unique_together = ['supply_link', 'parameter']
        verbose_name = _('supply link')
        verbose_name_plural = _('supply links')

    @cached_property
    def param_name(self):
        """

        """
        return self.parameter.param_name

    @property
    def mapping(self):
        """

        """
        return {self.field_name: self.param_name}

    def validate(self, data):
        """

        """
        value = data.get(self.field_name)
        return self.parameter.validate(value)
