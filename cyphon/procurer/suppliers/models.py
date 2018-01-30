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
Defines a |Supplier| model for third-party platforms that fulfill
API requests through |Requisitions|.

============================  ================================================
Class                         Description
============================  ================================================
:class:`~Supplier`            Defines a third-party platform.
============================  ================================================

"""

# third party
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.platforms.models import Platform, PlatformManager


class Supplier(Platform):
    """A third-party |Platform| that fulfills |Requisitions|.

    Attributes
    ----------
    name : str
        The name of the :doc:`/modules/platforms` subpackage for
        accessing a REST API.

    enabled : bool
        Whether the |Supplier| is available for use.

    """

    objects = PlatformManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('supplier')
        verbose_name_plural = _('suppliers')
