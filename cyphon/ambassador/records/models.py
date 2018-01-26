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
Defines a |Record| base class for storing a record of an API call.

=======================  ===================================================
Class                    Description
=======================  ===================================================
:class:`~Record`         Stores a record of an API call.
:class:`~RecordManager`  A model manager for |Records|.
=======================  ===================================================

Note
----
The |Record| class is the basis for the |Dispatch|, |Invoice|, and
|Manifest| classes.

"""

# third party
from django.db import models
from django.utils.functional import cached_property

# local
from ambassador.stamps.models import Stamp
from cyphon.models import SelectRelatedManager


class RecordManager(SelectRelatedManager):
    """A model manager for |Records|."""

    pass


class Record(models.Model):
    """Provides a record of an API call.

    Attributes
    ----------
    stamp : Stamp
        A |Stamp| recording the details of the API call.

    Note
    ----
    Much of the information about the API call is stored in the
    |Record|'s |Stamp|, rather than in the |Record| itself. This is
    to permit development of |Record| subclasses -- such as |Dispatches|,
    |Invoices|, and |Manifests| -- that have more specialized attributes,
    while still allowing information common to all API calls to be
    stored in the same database table -- the one for |Stamps|.

    """

    stamp = models.ForeignKey(
        Stamp,
        null=True,
        blank=True,
        verbose_name='stamp'
    )

    class Meta(object):
        """Metadata options."""

        abstract = True

    @cached_property
    def issued_by(self):
        """The |AppUser| who issued the API call."""
        return self.get_user()

    @cached_property
    def status_code(self):
        """A |str| of the status code of the API response."""
        return self.get_status_code()

    @cached_property
    def response_msg(self):
        """A |str| message returned in the API response."""
        return self.stamp.notes

    def get_status_code(self):
        """Get the status code of the API response.

        Returns
        -------
        str
            The status code of the API response.

        """
        return self.stamp.status_code

    get_status_code.short_description = 'status code'

    def get_user(self):
        """Get the |AppUser| who issued the API call.

        Returns
        -------
        |AppUser|
            The |AppUser| who issued the API call.

        """
        return self.stamp.user

    get_user.short_description = 'user'

    def get_endpoint(self):
        """Get the |Endpoint| associated with the |Record|.

        Returns
        -------
        |Endpoint|
            The |Endpoint| associated with the |Record|.

        """
        return self.stamp.endpoint

    def finalize(self, cargo):
        """Update the |Record|'s |Stamp| with the response from the API.

        Parameters
        ----------
        cargo : |Cargo|
              The |Cargo| returned by a |Transport| after calling an API.

        Returns
        -------
        |Record|
            self

        """
        self.stamp.finalize(status_code=cargo.status_code, notes=cargo.notes)
        return self
