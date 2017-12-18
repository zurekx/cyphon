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

# third party
from rest_framework import status

# local
from alerts.models import Alert
from appusers.models import AppUser
from procurer.procurements.models import Procurement
from tests.api_tests import CyphonAPITestCase
from tests.fixture_manager import get_fixtures


class ProcurementAPITests(CyphonAPITestCase):
    """
    Tests REST API endpoints for Procurements.
    """

    fixtures = get_fixtures(['alerts', 'procurements', 'quartermasters'])

    model_url = 'procurements/'
    obj_url = '1/'

    def setUp(self):
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
        self.assertEqual(response.data['count'], 1)

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

    # def test_process(self):
    #     """
    #     Tests the GET /api/v1/procurements/process/ REST API endpoint.
    #     """
    #     data = {'url': 'example.com'}
    #     response = self.post_to_api('1/process/', data=data, is_staff=False)
    #     # self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     print('response.data', response.data)
    #     # self.assertEqual(response.data['count'], 0)
