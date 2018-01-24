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
Defines a |Quartermaster| model for getting and processing data from a
series of API requests.

============================  ================================================
Class                         Description
============================  ================================================
:class:`~Quartermaster`       Provides credentials for a |Convoy|.
============================  ================================================

"""

# third party
from django.db import models
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.emissaries.models import Emissary, EmissaryManager
from procurer.requisitions.models import Requisition


class Quartermaster(Emissary):
    """Handles a |Passport| and |Visa| for use with a |Convoy|.

    Attributes
    ----------
    name : str
        The iname of the Quartermaster.

    passport : Passport
        The |Passport| used to access the `endpoints`.

    visa : Visa
        The |Visa| used to define a rate limit when accessing any of the
        `endpoints`.

    endpoints : `QuerySet` of `Requisitions`
        A |QuerySet| of |Requisitions| that the |Quartermaster| can help
        execute.

    """
    endpoints = models.ManyToManyField(
        Requisition,
        verbose_name=_('requisition'),
        related_name='emissaries',
        related_query_name='emissary'
    )

    objects = EmissaryManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('quartermaster')
        verbose_name_plural = _('quartermasters')
