# -*- coding: utf-8 -*-
# Copyright 2017 Dunbar Cybersecurity.
#
# This file is part of Cyphon Engine.
#
# Cyphon Engine is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Cyphon Engine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
"""
Configures exceptions for the :ref:`SupplyChains<supplychains>` app.

==============================  ======================================
Class                           Description
==============================  ======================================
:class:`~SupplyChainError`      An Exception for |SupplyChain| errors.
==============================  ======================================

"""


class SupplyChainError(Exception):
    """Exception raised for errors in the execution of a SupplyChain.

    Attributes
    ----------
    msg : str
        Explanation of the error.

    """

    def __init__(self, msg=None):
        super(SupplyChainError, self).__init__(msg)
        self.msg = msg
