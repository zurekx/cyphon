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
Defines a |SupplyChain| and related models to chain together
API requests.

============================  ================================================
Class                         Description
============================  ================================================
:class:`~SupplyChain`         Chains together API requests.
:class:`~SupplyChainManager`  Model manager for |SupplyChains|.
:class:`~SupplyLink`          Defines an API call within a |SupplyChain|.
:class:`~SupplyLinkManager`   Model manager for |SupplyLinks|.
:class:`~FieldCoupling`       Maps a data field to an API parameter.
============================  ================================================

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
from cyphon.models import GetByNameManager
from cyphon.choices import TIME_UNIT_CHOICES
from cyphon.tasks import start_supplylink
from procurer.requisitions.models import Requisition, Parameter
import utils.dateutils.dateutils as dt
from .exceptions import SupplyChainError

_LOGGER = logging.getLogger(__name__)


class SupplyChainManager(GetByNameManager):
    """Manage |SupplyChain| objects.

    Adds methods to the default Django model manager.
    """

    def filter_by_user(self, user, queryset=None):
        """Get |SupplyChains| that can be executed by the given user.

        Ensures that every |SupplyLink| in the the |SupplyChain| can be
        executed by the given user.

        Returns
        -------
        |Queryset|
            A |Queryset| of |SupplyChains| can be executed by the given
            user.

        """
        if queryset is not None:
            supplychain_qs = queryset
        else:
            supplychain_qs = self.get_queryset()

        excluded_supplylinks = SupplyLink.objects.exclude_by_user(user)
        return supplychain_qs.exclude(supply_link__in=excluded_supplylinks)


class SupplyChain(models.Model):
    """Links together a series of API requests.

    Attributes
    ----------
    name : str
        The name of the |SupplyChain|.

    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('name')
    )

    objects = SupplyChainManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supply chain')
        verbose_name_plural = _('supply chains')

    def __str__(self):
        """String representation of a |SupplyChain|."""
        return self.name

    @cached_property
    def _first_link(self):
        """The first |SupplyLink| in the |SupplyChain|."""
        return self.supply_links.first()

    @cached_property
    def _last_link(self):
        """The last |SupplyLink| in the |SupplyChain|."""
        return self.supply_links.last()

    @property
    def platform(self):
        """The |Platform| for the last |SupplyLink| in the |SupplyChain|."""
        return self._last_link.platform

    @property
    def input_fields(self):
        """|dict| of field names and field types for the |SupplyChain| input.

        Returns a dictionary in which keys are the names of input fields
        and the values are the field types.
        """
        return self._first_link.input_fields

    @property
    def errors(self):
        """A |list| of errors associated with the |SupplyLinks|."""
        errors = []
        supply_links = self.supply_links.all()

        if supply_links:
            for supply_link in self.supply_links.all():
                if supply_link.errors:
                    errors += supply_link.errors
        else:
            errors = ['SupplyChain has no SupplyLinks.']

        return errors

    def validate_input(self, data):
        """Return |True| if the data is valid input for the |SupplyChain|.

        Parameters
        ----------
        data : dict
            The data to validate as input for the |SupplyChain|.

        Returns
        -------
        |True|
            Returns |True| if the data is valid input for the |SupplyChain|.
            (Otherwise, raises a |SupplyChainError|.)

        Raises
        ------
        |SupplyChainError|
            If the data is not valid input for the |SupplyChain|.

        """
        return self._first_link.validate_input(data)

    def start(self, supply_order):
        """Fulfill a |SupplyOrder| using the |SupplyChain|.

        Parameters
        ----------
        supply_order : |SupplyOrder|
            The |SupplyOrder| that is supplying the input data for the
            |SupplyChain| and storing the result of the API request.

        Returns
        -------
        dict or None
            Returns a dictionary of results if the |SupplyChain| was
            executed successfully. Otherwise, returns None.

        Notes
        -----
        As a side effect, this method will also create |Manifests| that
        record the API calls made by the SupplyLinks in the |SupplyChain|.

        """
        # use object ids instead of objects, which aren't JSON serializable
        # and can't be used in celery tasks
        supply_links = self.supply_links.all()
        supply_link_ids = list(supply_links.values_list('pk', flat=True))

        links = [start_supplylink.s(supply_order.input_data,
                                    supply_link_ids[0], supply_order.id)]
        links += [
            start_supplylink.s(supply_link_id, supply_order.id)
            for supply_link_id in supply_link_ids[1:]
        ]
        result = chain(*links)()
        return result.get()


class SupplyLinkManager(GetByNameManager):
    """Manage |SupplyLink| objects.

    Adds methods to the default Django model manager.
    """

    def filter_by_user(self, user, queryset=None):
        """Get |SupplyLinks| that can be executed by the given user.

        Returns
        -------
        |Queryset|
            A |Queryset| of |SupplyLinks| can be executed by the given
            user.

        """
        if queryset is not None:
            supplylink_qs = queryset
        else:
            supplylink_qs = self.get_queryset()

        has_user = models.Q(requisition__emissary__passport__users=user)
        is_public = models.Q(requisition__emissary__passport__public=True)
        return supplylink_qs.filter(has_user | is_public).distinct()

    def exclude_by_user(self, user, queryset=None):
        """Get |SupplyLinks| that cannot be executed by the given user.

        Returns
        -------
        |Queryset|
            A |Queryset| of |SupplyLinks| can be executed by the given
            user.

        """
        if queryset is not None:
            supplylink_qs = queryset
        else:
            supplylink_qs = self.get_queryset()

        available_supplylinks = self.filter_by_user(user)
        ids = available_supplylinks.values_list('id', flat=True)
        return supplylink_qs.exclude(id__in=ids)


class SupplyLink(models.Model):
    """Defines an API call within a |SupplyChain|.

    Attributes
    ----------
    supply_chain : SupplyChain
        The |SupplyChain| associated with the |SupplyLink|.

    requisition : Requisition
        The |Requisition| associated with the |SupplyLink|.

    position : int
        An |int| representing the order of the |SupplyLink| in a
        |SupplyChain|. |SupplyLinks| are evaluated in ascending order
        (the lowest rank first)

    wait_time : int
        A delay time to wait before processing a request to the API.

    time_unit : str
        The time units for the :attr:`~SupplyLink.wait_time`. Possible
        values are constrained to |TIME_UNIT_CHOICES|.

    """

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('name')
    )
    supply_chain = models.ForeignKey(
        SupplyChain,
        related_name='supply_links',
        related_query_name='supply_link',
        verbose_name=_('supply chain'),
        help_text=_('The Supply Chain to which this Supply Link belongs.')
    )
    requisition = models.ForeignKey(
        Requisition,
        verbose_name=_('requisition'),
        help_text=_('The Requisition that defines the API request being made.')
    )
    position = models.IntegerField(
        default=0,
        verbose_name=_('position'),
        help_text=_('An integer representing the order of this Supply '
                    'Link in the Supply Chain.')
    )
    wait_time = models.IntegerField(
        default=0,
        verbose_name=_('wait interval'),
        help_text=_('An integer representing the time to wait before '
                    'executing the Requisition following execution of '
                    'the previous step in the Supply Chain.')
    )
    time_unit = models.CharField(
        max_length=3,
        default='m',
        choices=TIME_UNIT_CHOICES,
        verbose_name=_('time unit'),
        help_text=_('Units for the wait time.')
    )

    objects = SupplyLinkManager()

    class Meta(object):
        """Metadata options."""

        ordering = ['supply_chain', 'position']
        unique_together = ['supply_chain', 'position']
        verbose_name = _('supply link')
        verbose_name_plural = _('supply links')

    def __str__(self):
        """A string representation of the |SupplyLink|."""
        return self.name

    @cached_property
    def input_fields(self):
        """|dict| of field names and field types for the |SupplyLink| input.

        Returns a dictionary in which keys are the names of input fields
        and the values are the field types.
        """
        input_fields = {}
        for field_coupling in self.field_couplings.all():
            input_fields.update(field_coupling.input_field)
        return input_fields

    @cached_property
    def coupling(self):
        """|dict| of input field names mapped to parameter names.

        Returns a dictionary in which the keys are field names that
        correspond to the keys of input data and the values are the
        names of the parameters for which those fields will supply
        values.
        """
        coupling = {}
        for field_coupling in self.field_couplings.all():
            coupling.update(field_coupling.mapping)
        return coupling

    @property
    def countdown_seconds(self):
        """The number of seconds to wait before processing an API request."""
        return dt.convert_time_to_seconds(self.wait_time, self.time_unit)

    @property
    def platform(self):
        """The |Platform| associated with the |SupplyLink|'s |Requisition|."""
        return self.requisition.platform

    @cached_property
    def _coupling_parameters(self):
        """A list of Parameters associated with the |SupplyLink|."""
        return [coupling.parameter for coupling in self.field_couplings.all()]

    @cached_property
    def _required_parameters(self):
        """A QuerySet of required Parameters for the |SupplyLink|."""
        return self.requisition.required_parameters

    @property
    def errors(self):
        """A |list| of errors for missing required |FieldCouplings|."""
        errors = []
        for req_param in self._required_parameters:
            if req_param not in self._coupling_parameters:
                errors.append('A FieldCoupling is missing for Parameter %s, '
                              'which is required.' % req_param.pk)
        return errors

    def _get_params(self, data):
        """Return a dict of parameter values based on input data.

        Takes a dictionary of input data and returns a dictionary that
        maps their values to parameter names.
        """
        params = {}
        for (field_name, param_name) in self.coupling.items():
            params[param_name] = data.get(field_name)
        return params

    def _create_transport(self, user):
        """Create a Convoy for the given user."""
        return self.requisition.create_request_handler(user=user)

    def validate_input(self, data):
        """Return |True| if the data is valid input for the |SupplyChain|.

        Parameters
        ----------
        data : dict
            The data to validate as input for the |SupplyChain|.

        Returns
        -------
        |True|
            Returns |True| if the data is valid input for the
            |SupplyChain|. (Otherwise, raises a |SupplyChainError|.)

        Raises
        ------
        |SupplyChainError|
            If the data is not valid input for the |SupplyChain|.

        """
        is_valid = True
        invalid_couplings = []
        for coupling in self.field_couplings.all():
            if not coupling.validate_input(data):
                is_valid = False
                invalid_couplings.append('FieldCoupling %s' % coupling.pk)

        if not is_valid:
            error_msg = ('The following couplings were invalid: %s'
                         % invalid_couplings)
            raise SupplyChainError(error_msg)

        return is_valid

    def process(self, data, supply_order):
        """Submit an API request and return the result.

        Parameters
        ----------
        data : |dict|
            A dictionary of data used to construct the API request.

        supply_order : |SupplyOrder|
            The |SupplyOrder| associated with the API request.

        Returns
        -------
        |dict| or |None|
            The data returned from the API.

        Raises
        ------
        |SupplyChainError|
            If the data is not valid input for the SupplyLink.

        Notes
        -----
        If the API request returns a response, a |Manifest| for the API
        call will be created and associated with the |SupplyOrder|.

        """
        if data is None:
            return

        self.validate_input(data)

        params = self._get_params(data)
        transport = self._create_transport(supply_order.user)
        time.sleep(self.countdown_seconds)
        transport.run(params)

        if transport.record:
            transport.record.supply_order = supply_order
            transport.record.save()

        if transport.cargo:
            return transport.cargo.data
        else:
            _LOGGER.error('An error occurred while executing SupplyLink '
                          '%s for SupplyOrder %s.', self.pk, supply_order.pk)


class FieldCoupling(models.Model):
    """Maps an input field name to an API request parameter.

    Attributes
    ----------
    supply_link : SupplyLink
        The |SupplyLink| associated with the Coupling.

    field_name : str
        The name of an input field storing the value for the
        :attr:`~FieldCoupling.parameter`.

    parameter : Parameter
        The |Parameter| that will be supplied a value.

    """

    supply_link = models.ForeignKey(
        SupplyLink,
        related_name='field_couplings',
        related_query_name='field_coupling',
        verbose_name=_('supply link'),
        help_text=_('The Supply Link that uses this Field Coupling.')
    )
    parameter = models.ForeignKey(
        Parameter,
        related_name='field_couplings',
        related_query_name='field_coupling',
        verbose_name=_('parameter'),
        help_text=_('The target parameter in the API request.')
    )
    field_name = models.CharField(
        max_length=64,
        verbose_name=_('field name'),
        help_text=_('The name of the data field that will supply a value '
                    'for the parameter.')
    )

    class Meta(object):
        """Metadata options."""

        ordering = ['supply_link', 'parameter']
        unique_together = ['supply_link', 'parameter']
        verbose_name = _('field coupling')
        verbose_name_plural = _('field couplings')

    def __str__(self):
        """String representation of a |FieldCoupling|."""
        return '%s: %s' % (self.supply_link, self.parameter)

    @cached_property
    def _param_name(self):
        """The name of the API request parameter."""
        return self.parameter.param_name

    @cached_property
    def _param_type(self):
        """The data type of API request parameter."""
        return self.parameter.param_type

    @property
    def mapping(self):
        """A |dict| that maps the input field name to the parameter name."""
        return {self.field_name: self._param_name}

    @cached_property
    def input_field(self):
        """A |dict| that maps the input field name to the parameter type."""
        return {self.field_name: self._param_type}

    def validate_input(self, data):
        """Determine if the input data contains a valid parameter value.

        Parameters
        ----------
        data : dict
            A |dict| of input data.

        Returns
        -------
        bool
            Returns |True| if the data sontains a valid value for the
            parameter. Otherwise, returns |False|.

        """
        value = data.get(self.field_name)
        return self.parameter.validate(value)
