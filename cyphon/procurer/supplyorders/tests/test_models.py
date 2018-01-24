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

"""

# standard library
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

# third party
from django.test import TestCase
from testfixtures import LogCapture

# local
from alerts.models import Alert
from distilleries.models import Distillery
from procurer.supplyorders.models import SupplyOrder
from tests.fixture_manager import get_fixtures
from tests.mock import patch_find_by_id


class SupplyOrderTestCase(TestCase):
    """
    Tests the SupplyOrder class.
    """

    fixtures = get_fixtures(['supplyorders', 'quartermasters'])

    def setUp(self):
        self.supplyorder = SupplyOrder.objects.get(pk=1)

    def test_results_no_distillery(self):
        """
        Tests the results property when no distillery is associated with
        the SupplyOrder
        """
        self.supplyorder.distillery = None
        actual = self.supplyorder.results
        expected = {}
        self.assertEqual(actual, expected)

    def test_results_no_doc_id(self):
        """
        Tests the results property when no doc_id is associated with the
        SupplyOrder
        """
        self.supplyorder.doc_id = None
        actual = self.supplyorder.results
        expected = {}
        self.assertEqual(actual, expected)

    @patch_find_by_id({'foo': 'bar'})
    def test_results_w_data(self):
        """
        Tests the results property when the document associated with the
        SupplyOrder can be found.
        """
        actual = self.supplyorder.results
        expected = {'foo': 'bar'}
        self.assertEqual(actual, expected)

    @patch_find_by_id({})
    def test_results_no_data(self):
        """
        Tests the results property when the document associated with the
        SupplyOrder can't be found.
        """
        with LogCapture() as log_capture:
            actual = self.supplyorder.results
            expected = {}
            self.assertEqual(actual, expected)
            msg = ('The document associated with id %s cannot be found in %s.'
                   % (self.supplyorder.doc_id, self.supplyorder.distillery))
            log_capture.check(
                ('procurer.supplyorders.models', 'WARNING', msg),
            )

    def test_input_fields(self):
        """
        Tests the associate_alert property.
        """
        actual = self.supplyorder.input_fields
        expected = {'url': 'CharField'}
        self.assertEqual(actual, expected)

    def test_associate_alert(self):
        """
        Tests the associate_alert method.
        """
        alert = Alert.objects.get(pk=5)
        self.supplyorder.associate_alert(alert)
        supplyorder = SupplyOrder.objects.get(pk=self.supplyorder.pk)
        self.assertEqual(supplyorder.alert, alert)

    def test_update_result(self):
        """
        Tests the update_result method.
        """
        doc_id = '000'
        distillery = Distillery.objects.get(pk=4)
        self.supplyorder.update_result(distillery, doc_id)
        supplyorder = SupplyOrder.objects.get(pk=self.supplyorder.pk)
        self.assertEqual(supplyorder.distillery, distillery)
        self.assertEqual(supplyorder.doc_id, doc_id)

    def test_use_alert_data(self):
        """
        Tests the use_alert_data method.
        """
        test_data = {'url': 'testvalue', 'foo': 'bar'}
        self.supplyorder.alert.data = test_data
        self.supplyorder.use_alert_data()
        actual = self.supplyorder.input_data
        expected = {'url': 'testvalue'}
        self.assertEqual(actual, expected)

    def test_process(self):
        """
        Tests the process method.
        """
        self.supplyorder.procurement.process = Mock()
        self.supplyorder.process()
        self.supplyorder.procurement.process.assert_called_once_with(self.supplyorder)
