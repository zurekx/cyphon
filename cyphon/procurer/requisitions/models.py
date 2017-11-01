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
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.endpoints.models import Endpoint, EndpointManager
from cyphon.choices import FIELD_TYPE_CHOICES
from procurer.suppliers.models import Supplier


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

    url : str
        The URL for the REST API request.

    """
    platform = models.ForeignKey(Supplier, verbose_name=_('supplier'))

    url = models.URLField(verbose_name=_('URL'))

    objects = EndpointManager()

    class Meta(object):
        """Metadata options."""

        ordering = ['name']
        unique_together = ('platform', 'api_class')
        verbose_name = _('requisition')
        verbose_name_plural = _('requisitions')

    def _param_is_valid(self, field):
        """

        """
        pass

    def validate(self, form):
        """

        """
        pass

    def submit(self, form):
        """

        """
        pass
        # create polling celery task, passing in dispatch to be updated

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
        transport = self.create_request_handler(user=user, params=data)
        transport.run(data)
        return transport.record


class Parameter(models.Model):
    """

    """
    requisition = models.ForeignKey(Requisition, verbose_name=_('requisition'))
    param_name = models.CharField(
        max_length=64,
        verbose_name=_('parameter name')
    )
    param_type = models.CharField(
        max_length=64,
        choices=FIELD_TYPE_CHOICES,
        verbose_name=_('parameter type')
    )
    default = models.CharField(max_length=255, verbose_name=_('default value'))
    choices = ArrayField(
        ArrayField(models.CharField(max_length=255), size=2),
        verbose_name=_('choices')
    )
    required = models.BooleanField(default=False, verbose_name=_('required'))
    help_text = models.CharField(max_length=255, verbose_name=_('help text'))
    verbose_name = models.CharField(
        max_length=255,
        verbose_name=_('verbose name')
    )

    class Meta(object):
        """Metadata options."""

        verbose_name = _('parameter')
        verbose_name_plural = _('parameters')
        unique_together = ['requisition', 'param_name']

    def validate(self, value):
        """

        """
        pass
