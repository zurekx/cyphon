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
Tests views for Distilleries.
"""

# standard library
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

# third party
from celery.contrib.testing.worker import start_worker
from rest_framework import status

# local
from alerts.models import Alert
from appusers.models import AppUser
from cyphon.celeryapp import app
from procurer.supplychains.exceptions import SupplyChainError
from procurer.supplyorders.models import SupplyOrder
from tests.api_tests import CyphonAPITransactionTestCase, PassportMixin
from tests.fixture_manager import get_fixtures


class ProcurementAPITests(CyphonAPITransactionTestCase, PassportMixin):
    """
    Tests REST API endpoints for Procurements.
    """

    allow_database_queries = True

    fixtures = get_fixtures(['alerts', 'procurements', 'quartermasters'])

    model_url = 'procurements/'
    obj_url = '1/'

    @classmethod
    def setUpClass(cls):
        super(ProcurementAPITests, cls).setUpClass()
        # Start up celery worker
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        # Close worker
        cls.celery_worker.__exit__(None, None, None)
        super(ProcurementAPITests, cls).tearDownClass()

    def setUp(self):
        super(ProcurementAPITests, self).setUp()
        self.alert = Alert.objects.get(pk=2)
        self.user = AppUser.objects.get(id=2)

    def test_get_procurement(self):
        """
        Tests the GET /api/v1/procurements/1 REST API endpoint.
        """
        response = self.get_api_response(self.obj_url)
        expected = {
            'id': 1,
            'input_fields': {'url': 'CharField'},
            'name': 'VirusTotal URL Report',
            'munger': 3,
            'supply_chain': 2,
            'url': 'http://testserver/api/v1/procurements/1/',
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)

    def test_by_alert_w_data(self):
        """
        Tests the GET /api/v1/procurements/by-alert/ REST API endpoint
        for an Alert that has appropriate data and to which the user can
        access.
        """
        self.alert.data = {'url': 'example.com'}
        self.alert.save()
        response = self.get_api_response('by-alert/?id=2', is_staff=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_by_alert_no_alert(self):
        """
        Tests the GET /api/v1/procurements/by-alert/ REST API endpoint
        for an Alert that has appropriate data but to which the user
        does not have access.
        """
        self.alert.data = {'url': 'example.com'}
        self.alert.save()
        self.user = AppUser.objects.get(id=1)
        response = self.get_api_response('by-alert/?id=2', is_staff=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_by_alert_no_data(self):
        """
        Tests the GET /api/v1/procurements/by-alert/ REST API endpoint
        for an Alert that does not have appropriate data but to which
        the user has access.
        """
        response = self.get_api_response('by-alert/?id=2', is_staff=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    @patch('procurer.procurements.views.process_supplyorder')
    def test_process_success(self, mock_process):
        """
        Tests the POST /api/v1/procurements/process/ REST API endpoint.
        """
        data = {'url': 'http://dunbararmored.com'}
        self.assertEqual(SupplyOrder.objects.count(), 0)
        response = self.post_to_api('1/process/', data=data, is_staff=False)
        supplyorder_id = response.data.pop('id')
        response.data.pop('created_date')
        expected = {
            'results': {},
            'user': 2,
            'alert': None,
            'procurement': 1,
            'input_data': {
                'url': 'http://dunbararmored.com'
            },
            'doc_id': None,
            'distillery': None,
            'manifests': []
        }
        self.assertEqual(SupplyOrder.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        mock_process.delay.assert_called_once_with(supplyorder_id)

    @patch('procurer.procurements.views.process_supplyorder.delay',
           side_effect=SupplyChainError('an error occured'))
    def test_process_fail(self, mock_process):
        """
        Tests the GET /api/v1/procurements/process/ REST API endpoint
        when a SupplyChainError is raised.
        """
        data = {'url': 'http://dunbararmored.com'}
        response = self.post_to_api('1/process/', data=data, is_staff=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'msg': 'an error occured'})

    @patch('procurer.procurements.views.process_supplyorder')
    def test_process_alert_success(self, mock_process):
        """
        Tests the POST /api/v1/procurements/process-alert/ REST API endpoint
        for a successful request.
        """
        self.assertEqual(SupplyOrder.objects.count(), 0)
        self.alert.data = {'url': 'http://dunbararmored.com'}
        self.alert.save()
        response = self.post_to_api('1/process-alert/',
                                    data={'id': self.alert.id},
                                    is_staff=False)
        supplyorder_id = response.data.pop('id')
        response.data.pop('created_date')
        expected = {
            'results': {},
            'user': 2,
            'alert': 2,
            'input_data': {
                'url': 'http://dunbararmored.com'
            },
            'procurement': 1,
            'doc_id': None,
            'distillery': None,
            'manifests': []
        }
        self.assertEqual(SupplyOrder.objects.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected)
        mock_process.delay.assert_called_once_with(supplyorder_id)

    @patch('procurer.procurements.views.process_supplyorder.delay',
           side_effect=SupplyChainError('an error occured'))
    def test_process_alert_fail(self, mock_process):
        """
        Tests the POST /api/v1/procurements/process-alert/ REST API endpoint
        when a SupplyChainError is raised.
        """
        self.alert.data = {'url': 'http://dunbararmored.com'}
        self.alert.save()
        response = self.post_to_api('1/process-alert/',
                                    data={'id': self.alert.id},
                                    is_staff=False)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'msg': 'an error occured'})
