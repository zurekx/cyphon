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
import logging

# third party
from django.test import TestCase

# local
from distilleries.models import Distillery
from procurer.procurements.models import Procurement
from procurer.supplychains.exceptions import SupplyChainError
from procurer.supplyorders.models import SupplyOrder
from tests.fixture_manager import get_fixtures


class ProcurementManagerTestCase(TestCase):
    """
    Tests the ProcurementManager class.
    """

    fixtures = get_fixtures(['procurements'])

    def test_filter_by_user(self):
        """
        Tests the filter_by_user method.
        """
        pass

    def test_filter_by_alert(self):
        """
        Tests the filter_by_alert method.
        """
        pass


class ProcurementTestCase(TestCase):
    """
    Tests the Procurement class.
    """
    fixtures = get_fixtures(['procurements', 'supplyorders'])

    def setUp(self):
        """

        """
        super(ProcurementTestCase, self).setUp()
        self.procurement = Procurement.objects.get(pk=1)
        logging.disable(logging.ERROR)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    def test_validate_valid(self):
        """
        Tests the validate method.
        """
        data = {'url': 'https://example.com'}
        self.assertIs(self.procurement.validate(data), True)

    def test_validate_invalid(self):
        """
        Tests the validate method.
        """
        data = {'status': 400}
        with self.assertRaises(SupplyChainError):
            self.procurement.validate(data)

    def test_is_valid_true(self):
        """
        Tests the is_valid method for valid data.
        """
        data = {'url': 'https://example.com'}
        self.assertIs(self.procurement.is_valid(data), True)

    def test_is_valid_false(self):
        """
        Tests the is_valid method for invalid data.
        """
        data = {'status': 400}
        self.assertIs(self.procurement.is_valid(data), False)

    @patch('sifter.mungers.models.Distillery.save_data',
           return_value='123')
    @patch('procurer.supplychains.models.SupplyChain.start', return_value={'foo': 'bar'})
    def test_process(self, mock_start, mock_save):
        """
        Tests the process method.
        """
        supply_order = SupplyOrder.objects.get(id=1)
        result = self.procurement.process(supply_order)
        distillery = Distillery.objects.get_by_natural_key('elasticsearch.test_index.test_scan')
        mock_start.assert_called_once_with(supply_order)
        self.assertEqual(result.doc_id, '123')
        self.assertEqual(result.distillery, distillery)
