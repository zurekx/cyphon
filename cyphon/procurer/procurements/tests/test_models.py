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
    from unittest.mock import patch
except ImportError:
    from mock import patch
import logging

# third party
from django.test import TestCase

# local
from alerts.models import Alert
from ambassador.passports.models import Passport
from appusers.models import AppUser
from distilleries.models import Distillery
from procurer.procurements.models import Procurement
from procurer.supplychains.exceptions import SupplyChainError
from procurer.supplyorders.models import SupplyOrder
from tests.fixture_manager import get_fixtures


class ProcurementManagerTestCase(TestCase):
    """
    Tests the ProcurementManager class.
    """

    fixtures = get_fixtures(['alerts', 'procurements', 'quartermasters'])

    def setUp(self):
        super(ProcurementManagerTestCase, self).setUp()
        self.alert = Alert.objects.get(pk=2)
        self.user = AppUser.objects.get(pk=2)

    def test_filter_by_user_w_co(self):
        """
        Tests the filter_by_user method when the procurement is
        associated with the same company as the user.
        """
        filtered_qs = Procurement.objects.filter_by_user(self.user)
        self.assertEqual(filtered_qs.count(), 2)

    def test_filter_by_user_no_co(self):
        """
        Tests the filter_by_user method when the user is not associated
        with the company associated with the procurement.
        """
        user = AppUser.objects.get(pk=4)
        filtered_qs = Procurement.objects.filter_by_user(user)
        self.assertEqual(filtered_qs.count(), 1)

    def test_filter_by_user_staff(self):
        """
        Tests the filter_by_user method when the user is not associated
        with the company associated with the procurement but the user is
        staff.
        """
        user = AppUser.objects.get(pk=1)
        filtered_qs = Procurement.objects.filter_by_user(user)
        self.assertEqual(filtered_qs.count(), 3)

    def test_filter_by_user_no_passport(self):
        """
        Tests the filter_by_user method when the user is associated with
        a different company than the procurement.
        """
        passport = Passport.objects.get(pk=5)
        passport.public = False
        passport.save()
        filtered_qs = Procurement.objects.filter_by_user(self.user)
        self.assertEqual(filtered_qs.count(), 0)

    def test_filter_by_user_w_qs(self):
        """
        Tests the filter_by_user method when a QuerySet is supplied.
        """
        none_qs = Procurement.objects.none()
        filtered_qs = Procurement.objects.filter_by_user(self.user, none_qs)
        self.assertEqual(filtered_qs.count(), 0)

    def test_filter_by_alert_incompat(self):
        """
        Tests the filter_by_alert method for an incompatible alert.
        """
        filtered_qs = Procurement.objects.filter_by_alert(self.alert)
        self.assertEqual(filtered_qs.count(), 0)

    def test_filter_by_alert_incompat(self):
        """
        Tests the filter_by_alert method for a compatible alert.
        """
        self.alert.data = {'url': 'example.com'}
        self.alert.save()
        filtered_qs = Procurement.objects.filter_by_alert(self.alert)
        self.assertEqual(filtered_qs.count(), 3)

    def test_filter_by_alert_w_qs(self):
        """
        Tests the filter_by_alert method when a QuerySet is supplied.
        """
        none_qs = Procurement.objects.none()
        filtered_qs = Procurement.objects.filter_by_alert(self.alert, none_qs)
        self.assertEqual(filtered_qs.count(), 0)


class ProcurementTestCase(TestCase):
    """
    Tests the Procurement class.
    """
    fixtures = get_fixtures(['procurements', 'supplyorders'])

    def setUp(self):
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
