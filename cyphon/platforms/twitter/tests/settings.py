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
Tests the TwitterSearch class.
"""

# standard library
import logging

# third party
from django.conf import settings

# local
from tests.api_tests import settings_exist

TWITTER_SETTINGS = settings.TWITTER

_LOGGER = logging.getLogger(__name__)


if not settings_exist(TWITTER_SETTINGS):
    TWITTER_TESTS_ENABLED = False
    _LOGGER.warning('Twitter authentication credentials are missing, '
                    'so Twitter API tests will be skipped.')
else:
    TWITTER_TESTS_ENABLED = True
