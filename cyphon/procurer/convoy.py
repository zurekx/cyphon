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
Defines a |Convoy| model for processing |Requisitions|.

================  =======================================================
Class             Description
================  =======================================================
:class:`~Convoy`  A |Transport| subclass associated with a |Requisition|.
================  =======================================================

"""

# local
from ambassador.transport import Transport
from procurer.manifests.models import Manifest


class Convoy(Transport):
    """A |Transport| for a |Requisition|."""

    def create_record(self, stamp, obj):
        """Create a |Manifest| to record an API call and its response.

        Parameters
        ----------
        stamp : |Stamp|
            The |Stamp| assciated with an API call.

        obj : |dict|
            The data returned by the API call.

        Returns
        -------
        |Manifest|
            A |Manifest| recording an API call and its result.

        """
        return Manifest.objects.create(
            stamp=stamp,
            data=obj,
        )
