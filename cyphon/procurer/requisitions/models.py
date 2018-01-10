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
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.endpoints.models import Endpoint, EndpointManager
from cyphon.choices import FIELD_TYPE_CHOICES
from procurer.suppliers.models import Supplier
from utils.parserutils.parserutils import restore_type

_LOGGER = logging.getLogger(__name__)


class Requisition(Endpoint):
    """

    Attributes
    ----------
    api_module : str
        The name of the module that will handle the API request
        (i.e., the name of the Python file without the extension,
        e.g., 'handlers').

    api_class : str
        The name of the class that will handle the API request
        (e.g., 'SearchAPI').

    visa_required : bool
        Whether requests to the API endpoint are rate limited.
        If |True|, an |Emissary| must have a |Visa| to access the
        |Endpoint|. The |Visa| defines the rate limit that should
        apply to the |Emissary|'s |Passport| (API key).

    platform : |Supplier|
        The data platform which the API endpoint accesses.

    """

    platform = models.ForeignKey(Supplier, verbose_name=_('supplier'))

    objects = EndpointManager()

    class Meta(object):
        """Metadata options."""

        unique_together = ('platform', 'api_class')
        verbose_name = _('requisition')
        verbose_name_plural = _('requisitions')

    @property
    def required_parameters(self):
        """Get a QuerySet of required Parameters.

        Returns
        -------
        |QuerySet|
            A QuerySet of the Requisition's required Parameters.

        """
        return self.parameters.filter(required=True)

    def get_manifest(self, user, data):
        """

        Parameters
        ----------
        user : |AppUser|
            The user making the API request.

        data : |dict|
            A dictionary of data used to construct the API request.

        Returns
        -------
        |Manifest|
            A record of the API response.

        """
        transport = self.create_request_handler(user=user)
        transport.run(data)
        return transport.record


class ParameterManager(models.Manager):
    """Manage |Parameter| objects.

    Adds methods to the default Django model manager.
    """

    def get_by_natural_key(self, platform, api_class, param_name):
        """Get a |Context| by its natural key.

        Allows retrieval of a |Context| by its natural key instead of
        its primary key.

        Parameters
        ----------
        platform : str
            The name of the platform package.

        api_class : str
            The name of the API class.

        param_name : str
            The name of the parameter.

        Returns
        -------
        |Parameter|
            The |Parameter| associated with the natural key.

        """
        try:
            requisition_key = [platform, api_class]
            requisition = Requisition.objects.get_by_natural_key(*requisition_key)
            return self.get(requisition=requisition, param_name=param_name)
        except ObjectDoesNotExist:
            _LOGGER.error('%s %s %s %s does not exist',
                          self.model.__name__, platform, api_class, param_name)


class Parameter(models.Model):
    """

    """

    requisition = models.ForeignKey(
        Requisition,
        related_name='parameters',
        related_query_name='parameter',
        verbose_name=_('requisition'),
    )
    param_name = models.CharField(
        max_length=64,
        verbose_name=_('parameter name'),
        help_text=_('The name of the parameter in the API request.')
    )
    param_type = models.CharField(
        max_length=64,
        choices=FIELD_TYPE_CHOICES,
        verbose_name=_('parameter type'),
        help_text=_('The data type of the parameter.')
    )
    default = models.CharField(
        max_length=255,
        verbose_name=_('default value'),
        null=True,
        blank=True,
        help_text=_('The default value for the parameter.')
    )
    choices = ArrayField(
        ArrayField(models.CharField(max_length=255), size=2),
        verbose_name=_('choices'),
        null=True,
        blank=True,
        help_text=_('A list of choices for the parameter, '
                    'in the format: (value, label), (value, label)')
    )
    required = models.BooleanField(
        default=False,
        verbose_name=_('required'),
        help_text=_('Whether the paremeter is required to fulfill '
                    'the request.')
    )
    help_text = models.CharField(
        max_length=255,
        verbose_name=_('help text'),
        null=True,
        blank=True,
        help_text=_('An explanation of the parameter to help users '
                    'understand its purpose.')
    )
    verbose_name = models.CharField(
        max_length=255,
        verbose_name=_('verbose name'),
        null=True,
        blank=True,
        help_text=_('A human-readable name for the parameter.')
    )

    objects = ParameterManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        unique_together = ['requisition', 'param_name']

    def __str__(self):
        """String representation of a Parameter."""
        return '%s : %s' % (self.requisition, self.param_name)

    def save(self, *args, **kwargs):
        """
        Overrides the save() method to validate the default value.
        """
        if self.default is not None \
                and not self._validate_data_type(self.value):
            msg = _('Default value is incompatible with the parameter type.')
            raise ValidationError(msg)
        return super(Parameter, self).save(*args, **kwargs)

    def _validate_data_type(self, value):
        """

        """
        try:
            restore_type(field_type=self.param_type, value=value)
            return True
        except ValueError:
            return False

    def validate(self, value):
        """

        """
        if value in [None, '']:
            return not self.required
        else:
            return self._validate_data_type(value)
