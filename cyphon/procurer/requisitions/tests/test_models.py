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
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

# third party
from django.test import TestCase
from testfixtures import LogCapture

# local
from appusers.models import AppUser
from procurer.requisitions.models import Requisition, Parameter
from tests.fixture_manager import get_fixtures


class RequisitionBaseTestCase(TestCase):
    """
    Base class for testing models in the Requisitions app.
    """

    fixtures = get_fixtures(['requisitions', 'users'])

    def setUp(self):
        self.requisition = Requisition.objects.get(pk=1)
        self.parameter = Parameter.objects.get(pk=1)


class RequisitionTestCase(RequisitionBaseTestCase):
    """
    Tests the Requisition model.
    """

    def test_required_parameters(self):
        """
        Tests the required_parameters property.
        """
        params = self.requisition.required_parameters
        self.assertEqual(params.count(), 1)
        self.assertEqual(params[0].pk, 1)

    def test_get_manifest(self):
        """
        Tests the get_manifest method.
        """
        mock_transport = Mock()
        user = AppUser.objects.get(pk=1)
        data = {'foo': 'bar'}
        with patch('procurer.requisitions.models.Endpoint.create_request_handler',
                   return_value=mock_transport) as mock_handler:
            result = self.requisition.get_manifest(user, data)
            mock_handler.assert_called_once_with(user=user)
            mock_transport.run.assert_called_once_with(data)
            self.assertEqual(result, mock_transport.record)


class ParameterManagerTestCase(RequisitionBaseTestCase):
    """
    Tests the ParameterManager class.
    """

    def test_get_by_natural_key(self):
        """
        Tests the get_by_natural_key method.
        """
        param = Parameter.objects.get_by_natural_key('virustotal', 'UrlScan', 'url')
        self.assertEqual(param, self.parameter)

    def test_get_by_nk_failure(self):
        """
        Tests the get_by_natural_key method.
        """
        with LogCapture() as log_capture:
            result = Parameter.objects.get_by_natural_key('foobar', 'foo', 'bar')
            self.assertEqual(result, None)
            log_capture.check(
                ('ambassador.endpoints.models',
                 'ERROR',
                 'Requisition for "foobar foo" does not exist'),
                ('procurer.requisitions.models',
                 'ERROR',
                 'Parameter foobar foo bar does not exist'),
            )


class ParameterTestCase(RequisitionBaseTestCase):
    """
    Tests the Parameter model.
    """

    def test_str(self):
        """
        Tests the __str__ method.
        """
        actual = str(self.parameter)
        expected = 'Virustotal UrlScan : url'
        self.assertEqual(actual, expected)

    def test_validate_null_required(self):
        """
        Tests the validate method with a null value for a required
        parameter.
        """
        data = None
        actual = self.parameter.validate(data)
        expected = False
        self.assertEqual(actual, expected)

    def test_validate_null_optional(self):
        """
        Tests the validate method with a null value for an optional
        parameter.
        """
        parameter = Parameter.objects.get(pk=2)
        data = None
        actual = parameter.validate(data)
        expected = True
        self.assertEqual(actual, expected)

    def test_validate_empty_str_req(self):
        """
        Tests the validate method with an empty string for a required
        parameter.
        """
        data = ''
        actual = self.parameter.validate(data)
        expected = False
        self.assertEqual(actual, expected)

    def test_validate_empty_str_optnl(self):
        """
        Tests the validate method with an empty string for an optional
        parameter.
        """
        parameter = Parameter.objects.get(pk=2)
        data = ''
        actual = parameter.validate(data)
        expected = True
        self.assertEqual(actual, expected)

    def test_validate_valid(self):
        """
        Tests the validate method for a valid dictionary.
        """
        data = 'foobar'
        actual = self.parameter.validate(data)
        expected = True
        self.assertEqual(actual, expected)

    def test_validate_invalid(self):
        """
        Tests the validate method for an invalid dictionary.
        """
        parameter = Parameter.objects.get(pk=2)
        data = 'foobar'
        actual = parameter.validate(data)
        expected = False
        self.assertEqual(actual, expected)
