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
# from django.db import models

# local
from ambassador.transport import Cargo, Transport
from procurer.manifests.models import Manifest
# from cyphon.transaction import close_old_connections
# from sifter.datasifter.datachutes.models import DataChute


class Convoy(Transport):
    """

    """

    def create_record(self, stamp, obj):
        """
        Create a record of the response

        Parameters
        ----------
        stamp : |Stamp|

        obj : |dict|


        Returns
        -------
        None

        """
        return Manifest.objects.create(
            stamp=stamp,
            data=obj,
        )
