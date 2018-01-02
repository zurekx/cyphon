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
    from unittest.mock import call, patch
except ImportError:
    from mock import call, patch

# third party
from celery.contrib.testing.worker import start_worker
from django.test import TestCase, TransactionTestCase
import six
from testfixtures import LogCapture

# local
from appusers.models import AppUser
from cyphon.celeryapp import app
from procurer.supplychains.exceptions import SupplyChainError
from procurer.supplychains.models import FieldCoupling, SupplyChain, SupplyLink
from procurer.supplyorders.models import SupplyOrder
from procurer.requisitions.models import Parameter
from tests.fixture_manager import get_fixtures


class SupplyChainBaseTestCase(TestCase):
    """

    """

    fixtures = get_fixtures(['supplychains', 'supplyorders', 'quartermasters'])

    def setUp(self):
        self.supplychain = SupplyChain.objects.get_by_natural_key(
            'VirusTotal URL Scan & Report')


class SupplyChainManagerTestCase(SupplyChainBaseTestCase):
    """
    Tests the SupplyChainManager class.
    """

    def test_filter_by_user_no_qs(self):
        """
        Tests the filter_by_user method when a QuerySet is not provided.
        """
        user = AppUser.objects.get(pk=2)
        supplychains = SupplyChain.objects.filter_by_user(user=user)
        self.assertEqual(supplychains.count(), 2)

        user = AppUser.objects.get(pk=3)
        supplychains = SupplyChain.objects.filter_by_user(user=user)
        self.assertEqual(supplychains.count(), 1)

    def test_filter_by_user_w_qs(self):
        """
        Tests the filter_by_user method when a QuerySet is provided.
        """
        supplychain_qs = SupplyChain.objects.exclude(pk=1)
        user = AppUser.objects.get(pk=2)
        supplychains = SupplyChain.objects.filter_by_user(user, supplychain_qs)
        self.assertEqual(supplychains.count(), 1)

        user = AppUser.objects.get(pk=3)
        supplychains = SupplyChain.objects.filter_by_user(user, supplychain_qs)
        self.assertEqual(supplychains.count(), 0)


class SupplyChainTestCase(SupplyChainBaseTestCase):
    """
    Tests the SupplyChain class.
    """

    fixtures = get_fixtures(['supplychains', 'supplyorders', 'quartermasters'])

    def setUp(self):
        self.supplychain = SupplyChain.objects.get_by_natural_key(
            'VirusTotal URL Scan & Report')

    def test_platform(self):
        """
        Tests the platform property.
        """
        actual = self.supplychain.platform
        expected = SupplyLink.objects.get(pk=2).platform
        self.assertEqual(actual, expected)

    def test_input_fields(self):
        """
        Tests the input_fields property.
        """
        actual = self.supplychain.input_fields
        expected = SupplyLink.objects.get(pk=1).input_fields
        self.assertEqual(actual, expected)

    def test_errors_no_supplylinks(self):
        """
        Tests the error property for a SupplyChain with no SupplyLinks.
        """
        supplychain = SupplyChain.objects.create(name='foobar')
        actual = supplychain.errors
        expected = ['SupplyChain has no SupplyLinks.']
        self.assertEqual(actual, expected)

    def test_errors_invalid_supplylink(self):
        """
        Tests the error property for a SupplyChain with an invalid SupplyLink.
        """
        parameter = Parameter.objects.get(pk=3)
        parameter.required = True
        parameter.save()
        actual = self.supplychain.errors
        expected = ['A FieldCoupling is missing for the required parameter '
                    '<Parameter: 3>.']
        self.assertEqual(actual, expected)

    def test_errors_for_valid_chain(self):
        """
        Tests the error property for a valid SupplyChain.
        """
        actual = self.supplychain.errors
        expected = []
        self.assertEqual(actual, expected)

    def test_validate_input_valid(self):
        """
        Tests the validate_input method for valid input.
        """
        data = {'url': 'foobar'}
        actual = self.supplychain.validate_input(data)
        expected = True
        self.assertEqual(actual, expected)

    def test_validate_input_invalid(self):
        """
        Tests the validate_input method for invalid input.
        """
        data = {'foobar': 'url'}
        msg = "The following couplings were invalid: \['<FieldCoupling: 2>'\]"
        with six.assertRaisesRegex(self, SupplyChainError, msg):
            self.supplychain.validate_input(data)


class SupplyChainTransactionTestCase(TransactionTestCase):
    """
    Tests the SupplyChain class.
    """

    allow_database_queries = True

    fixtures = get_fixtures(['supplychains', 'supplyorders', 'quartermasters'])

    @classmethod
    def setUpClass(cls):
        super(SupplyChainTransactionTestCase, cls).setUpClass()

        # Start up celery worker
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        # Close worker
        cls.celery_worker.__exit__(None, None, None)
        super(SupplyChainTransactionTestCase, cls).tearDownClass()

    def setUp(self):
        self.supplychain = SupplyChain.objects.get_by_natural_key(
            'VirusTotal URL Scan & Report')

    @patch('procurer.supplychains.models.SupplyLink.process',
           return_value={'url': 'foobar'})
    def test_start_success(self, mock_process):
        """

        """
        supplyorder = SupplyOrder.objects.get(pk=1)
        self.supplychain.start(supplyorder)
        mock_process.assert_has_calls([
            call({'url': 'http://dunbararmored.com'}, supplyorder),
            call({'url': 'foobar'}, supplyorder)
        ])

    def test_start_fail(self):
        """

        """
        pass


class SupplyLinkManagerTestCase(SupplyChainBaseTestCase):
    """
    Tests the SupplyLinkManager class.
    """

    def test_filter_by_user(self):
        """

        """
        pass

    def test_exclude_by_user(self):
        """

        """
        pass


class SupplyLinkTestCase(TestCase):
    """
    Tests the SupplyLink class.
    """

    def test_str(self):
        """

        """
        pass

    def test_input_fields(self):
        """

        """
        pass

    def test_coupling(self):
        """

        """
        pass

    def test_countdown_seconds(self):
        """

        """
        pass

    def test_platform(self):
        """

        """
        pass

    def test_errors(self):
        """

        """
        pass

    def test_validate_input(self):
        """

        """
        pass

    def test_process(self):
        """

        """
        pass


class FieldCouplingTestCase(SupplyChainBaseTestCase):
    """
    Tests the FieldCoupling class.
    """

    def test_mapping(self):
        """

        """
        pass

    def test_input_field(self):
        """

        """
        pass

    def test_validate_input(self):
        """

        """
        pass
