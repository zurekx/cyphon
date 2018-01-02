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
from appusers.models import AppUser
from tests.api_tests import CyphonAPITransactionTestCase, PassportMixin
from tests.fixture_manager import get_fixtures
from tests.mock import patch_find_by_id


class SupplyOrderAPITests(CyphonAPITransactionTestCase, PassportMixin):
    """
    Tests REST API endpoints for SupplyOrders.
    """

    fixtures = get_fixtures(['supplyorders', 'manifests'])

    model_url = 'supplyorders/'
    obj_url = '1/'

    def setUp(self):
        super(SupplyOrderAPITests, self).setUp()
        self.user = AppUser.objects.get(id=2)

    @patch_find_by_id({'foo': 'bar'})
    def test_get_supplyorder(self):
        """
        Tests the GET /api/v1/supplyorders/2 REST API endpoint.
        """
        response = self.get_api_response('2/', is_staff=False)
        results = response.json()
        expected = {
            'id': 2,
            'created_date': '2017-12-29T21:28:29.353954Z',
            'user': 2,
            'procurement': 1,
            'input_data': {
                'url': 'http://dunbararmored.com'
            },
            'alert': 1,
            'doc_id': '456',
            'distillery': 5,
            'results': {
                'foo': 'bar'
            },
            'manifests': [{
                'id': 1,
                'issued_by': {
                    'is_staff': True,
                    'id': 1,
                    'last_name': 'Smith',
                    'first_name': 'John',
                    'email': 'testuser1@testdomain.com',
                    'company': None
                },
                'data': {
                    'foo': 'bar'
                },
                'response_msg': None,
                'supply_order': 2,
                'status_code': '200'
            }],
        }
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(results, expected)

    @patch_find_by_id({'foo': 'bar'})
    def test_get_supplyorders_nonstaff(self):
        """
        Tests the GET /api/v1/supplyorders/ REST API endpoint for a user
        who is not staff.
        """
        response = self.get_api_response(is_staff=False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], 2)

    @patch_find_by_id({'foo': 'bar'})
    def test_get_supplyorders_staff(self):
        """
        Tests the GET /api/v1/supplyorders/ REST API endpoint for a user
        who is staff.
        """
        response = self.get_api_response(is_staff=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
