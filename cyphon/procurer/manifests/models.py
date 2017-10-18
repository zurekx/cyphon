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
from django.utils.translation import ugettext_lazy as _

# local
from ambassador.records.models import Record, RecordManager


class Manifest(Record):
    """Provides a record of an API call.

    Attributes
    ----------
    stamp : Stamp
        A |Stamp| recording the details of the API call.

    """

    # alert = models.ForeignKey(
    #     Alert,
    #     related_name='dispatches',
    #     related_query_name='dispatch'
    # )
    # data = JSONField(blank=True, null=True)

    objects = RecordManager()

    class Meta(object):
        """Metadata options."""

        verbose_name = _('Manifest')
        verbose_name_plural = _('manifests')
