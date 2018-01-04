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
    from unittest.mock import call, Mock, patch
except ImportError:
    from mock import call, Mock, patch

# third party
from celery.contrib.testing.worker import start_worker
from django.test import TestCase, TransactionTestCase
import six
from testfixtures import LogCapture

# local
from appusers.models import AppUser
from cyphon.celeryapp import app
from procurer.suppliers.models import Supplier
from procurer.supplychains.exceptions import SupplyChainError
from procurer.supplychains.models import FieldCoupling, SupplyChain, SupplyLink
from procurer.supplyorders.models import SupplyOrder
from procurer.requisitions.models import Parameter
from tests.fixture_manager import get_fixtures


class SupplyChainBaseTestCase(TestCase):
    """
    Base class for testing models in the supplychains app.
    """

    fixtures = get_fixtures(['supplychains', 'supplyorders', 'quartermasters'])

    def setUp(self):
        self.supplychain = SupplyChain.objects.get_by_natural_key(
            'VirusTotal URL Scan & Report')
        self.supplylink = SupplyLink.objects.get(pk=1)
        self.fieldcoupling = FieldCoupling.objects.get(pk=1)


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
        expected = ['A FieldCoupling is missing for Parameter 3, '
                    'which is required.']
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
        msg = "The following couplings were invalid: \['FieldCoupling 2'\]"
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
           side_effect=[{'url': 'foobar1'}, {'url': 'foobar2'}])
    def test_start_success(self, mock_process):
        """
        Tests the start method.
        """
        supplyorder = SupplyOrder.objects.get(pk=1)
        result = self.supplychain.start(supplyorder)
        mock_process.assert_has_calls([
            call({'url': 'http://dunbararmored.com'}, supplyorder),
            call({'url': 'foobar1'}, supplyorder)
        ])
        self.assertEqual(result, {'url': 'foobar2'})

    @patch('procurer.supplychains.models.SupplyLink.process',
           return_value=None)
    def test_start_failed(self, mock_process):
        """
        Tests the start method when a SupplyLink process returns None.
        """
        supplyorder = SupplyOrder.objects.get(pk=1)
        result = self.supplychain.start(supplyorder)
        mock_process.assert_has_calls([
            call({'url': 'http://dunbararmored.com'}, supplyorder),
            call(None, supplyorder)
        ])
        self.assertEqual(result, None)


class SupplyLinkManagerTestCase(SupplyChainBaseTestCase):
    """
    Tests the SupplyLinkManager class.
    """

    def test_filter_by_user_no_qs(self):
        """
        Tests the filter_by_user method when a QuerySet is not provided.
        """
        user = AppUser.objects.get(pk=2)
        supplylinks = SupplyLink.objects.filter_by_user(user=user)
        self.assertEqual(supplylinks.count(), 3)

        user = AppUser.objects.get(pk=3)
        supplylinks = SupplyLink.objects.filter_by_user(user=user)
        self.assertEqual(supplylinks.count(), 2)

    def test_filter_by_user_w_qs(self):
        """
        Tests the filter_by_user method when a QuerySet is provided.
        """
        supplylink_qs = SupplyLink.objects.exclude(pk=1)

        user = AppUser.objects.get(pk=2)
        supplylinks = SupplyLink.objects.filter_by_user(user, supplylink_qs)
        self.assertEqual(supplylinks.count(), 2)

        user = AppUser.objects.get(pk=3)
        supplylinks = SupplyLink.objects.filter_by_user(user, supplylink_qs)
        self.assertEqual(supplylinks.count(), 1)

    def test_exclude_by_user_no_qs(self):
        """
        Tests the exclude_by_user method when a QuerySet is not provided.
        """
        user = AppUser.objects.get(pk=2)
        supplylinks = SupplyLink.objects.exclude_by_user(user=user)
        self.assertEqual(supplylinks.count(), 0)

        user = AppUser.objects.get(pk=3)
        supplylinks = SupplyLink.objects.exclude_by_user(user=user)
        self.assertEqual(supplylinks.count(), 1)

    def test_exclude_by_user_w_qs(self):
        """
        Tests the exclude_by_user method when a QuerySet is provided.
        """
        supplylink_qs = SupplyLink.objects.exclude(pk=1)

        user = AppUser.objects.get(pk=2)
        supplylinks = SupplyLink.objects.exclude_by_user(user, supplylink_qs)
        self.assertEqual(supplylinks.count(), 0)

        user = AppUser.objects.get(pk=3)
        supplylinks = SupplyLink.objects.exclude_by_user(user, supplylink_qs)
        self.assertEqual(supplylinks.count(), 1)


class SupplyLinkTestCase(SupplyChainBaseTestCase):
    """
    Tests the SupplyLink class.
    """

    def test_str(self):
        """
        Tests the __str__ method.
        """
        self.assertEqual(str(self.supplylink), 'VirusTotal URL Report')

    def test_input_fields(self):
        """
        Tests the input_fields property.
        """
        actual = self.supplylink.input_fields
        expected = {'url': 'CharField'}
        self.assertEqual(actual, expected)

    def test_coupling(self):
        """
        Tests the coupling property.
        """
        actual = self.supplylink.coupling
        expected = {'url': 'resource'}
        self.assertEqual(actual, expected)

    def test_countdown_seconds(self):
        """
        Tests the countdown_seconds property.
        """
        supplylink = SupplyLink.objects.get(pk=3)
        actual = supplylink.countdown_seconds
        expected = 5.0
        self.assertEqual(actual, expected)

    def test_platform(self):
        """
        Tests the platform property.
        """
        actual = self.supplylink.platform
        expected = Supplier.objects.get_by_natural_key('virustotal')
        self.assertEqual(actual, expected)

    def test_errors_wo_errors(self):
        """
        Tests the errors property without errors.
        """
        actual = self.supplylink.errors
        expected = []
        self.assertEqual(actual, expected)

    def test_errors_w_errors(self):
        """
        Tests the errors property with errors.
        """
        FieldCoupling.objects.all().delete()
        actual = self.supplylink.errors
        expected = ['A FieldCoupling is missing for Parameter 1, '
                    'which is required.']
        self.assertEqual(actual, expected)

    def test_validate_input_valid(self):
        """
        Tests the validate_input method for valid input.
        """
        actual = self.supplylink.validate_input({'url': 'foobar'})
        expected = True
        self.assertEqual(actual, expected)

    def test_validate_input_invalid(self):
        """
        Tests the validate_input method for invalid input.
        """
        msg = "The following couplings were invalid: \['FieldCoupling 1'\]"
        with six.assertRaisesRegex(self, SupplyChainError, msg):
            self.supplylink.validate_input({'foobar': 'url'})

    @patch('procurer.supplychains.models.SupplyLink.requisition')
    @patch('procurer.supplychains.models.time.sleep')
    def test_process_success(self, mock_sleep, mock_req):
        """
        Tests the process method when the SupplyLink's Requisition
        returns a Cargo object.
        """
        supplyorder = SupplyOrder.objects.get(pk=1)
        data = {'url': 'foobar', 'foobar': 'url'}
        results = {'results': 'foobar'}
        mock_transport = Mock()
        mock_transport.cargo.data = results
        mock_req.create_request_handler = Mock(return_value=mock_transport)

        result = self.supplylink.process(data, supplyorder)
        self.assertEqual(result, results)
        mock_sleep.assert_called_once_with(self.supplylink.countdown_seconds)
        mock_transport.run.assert_called_once_with({'resource': 'foobar'})
        self.assertEqual(mock_transport.record.supply_order, supplyorder)
        mock_transport.record.save.assert_called_once_with()

    @patch('procurer.supplychains.models.SupplyLink.requisition')
    def test_process_fail(self, mock_req):
        """
        Tests the process method when the SupplyLink's Requisition does
        not return a Cargo object.
        """
        supplyorder = SupplyOrder.objects.get(pk=1)
        data = {'url': 'foobar', 'foobar': 'url'}
        mock_transport = Mock()
        mock_transport.cargo = None
        mock_req.create_request_handler = Mock(return_value=mock_transport)
        with LogCapture() as log_capture:
            result = self.supplylink.process(data, supplyorder)
            msg = ('An error occurred while executing SupplyLink 1 for '
                   'SupplyOrder 1.')
            log_capture.check(
                ('procurer.supplychains.models',
                 'ERROR',
                 msg),
            )
            self.assertEqual(result, None)


class FieldCouplingTestCase(SupplyChainBaseTestCase):
    """
    Tests the FieldCoupling class.
    """

    def test_mapping(self):
        """
        Tests the mapping property.
        """
        actual = self.fieldcoupling.mapping
        expected = {'url': 'resource'}
        self.assertEqual(actual, expected)

    def test_input_field(self):
        """
        Tests the input_field property.
        """
        actual = self.fieldcoupling.input_field
        expected = {'url': 'CharField'}
        self.assertEqual(actual, expected)

    def test_validate_input_valid(self):
        """
        Tests the validate_input method for valid input.
        """
        data = {'url': 'foobar'}
        actual = self.fieldcoupling.validate_input(data)
        expected = True
        self.assertEqual(actual, expected)

    def test_validate_input_invalid(self):
        """
        Tests the validate_input method for invalid input.
        """
        data = {}
        actual = self.fieldcoupling.validate_input(data)
        expected = False
        self.assertEqual(actual, expected)
