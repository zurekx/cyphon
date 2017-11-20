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
import time

# third party
from celery import chain
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

# local
# from bottler.containers.models import Container
from cyphon.models import GetByNameManager
from cyphon.choices import TIME_UNIT_CHOICES
from cyphon.tasks import start_supplylink
from procurer.requisitions.models import Requisition, Parameter
import utils.dateutils.dateutils as dt
from .exceptions import SupplyChainError

_LOGGER = logging.getLogger(__name__)


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

    def start(self, data, user):
        """

        """
        try:
            # use object ids instead of objects, which aren't JSON serializable
            # and can't be used in celery tasks
            id_list = list(self.supplylinks.all().values_list('pk', flat=True))
            links = [start_supplylink.s(data, id_list[0], user)]
            links += [
                start_supplylink.s(obj_id, user) for obj_id in id_list[1:]
            ]
            result = chain(*links)()
            return result.get()
        except SupplyChainError as error:
            _LOGGER.error('A SupplyChainError occurred: %s', error.msg)


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

    wait_time : int

    time_unit : str

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
    wait_time = models.IntegerField(
        default=0,
        verbose_name=_('wait interval')
    )
    time_unit = models.CharField(
        max_length=3,
        default='m',
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

    def __str__(self):
        """

        """
        return '<SupplyLink: %s>' % self.name

    @cached_property
    def coupling(self):
        """

        """
        coupling = {}
        for field_coupling in self.field_couplings.all():
            coupling.update(field_coupling.mapping)
        return coupling

    @property
    def countdown_seconds(self):
        """
        Returns the number of seconds bedore.
        """
        return dt.convert_time_to_seconds(self.wait_time, self.time_unit)

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
        return self.requisition.create_request_handler(user=user)

    def _validate(self, data):
        """

        """
        for coupling in self.field_couplings.all():
            if not coupling.validate(data):
                # TODO(LH): add message to exception
                raise SupplyChainError('The coupling %s was not valid'
                                       % coupling)
        return True

    def process(self, data, user):
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
        SupplyChainError

        """
        self._validate(data)

        params = self._get_params(data)
        transport = self._create_transport(user)
        time.sleep(self.countdown_seconds)
        transport.run(params)

        if transport.cargo:
            return transport.cargo.data
        else:
            # TODO(LH): add message to exception
            raise SupplyChainError()


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

    def __str__(self):
        """String representation of a FieldCoupling."""
        return '%s:%s' % (self.supply_link, self.parameter)

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
