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

# standard library
from unittest import skipUnless

# third party
from celery.contrib.testing.worker import start_worker
from django.test import TestCase, TransactionTestCase

# local
from ambassador.passports.models import Passport
from cyphon.celeryapp import app
from platforms.virustotal.handlers import UrlReport, UrlScan
from procurer.requisitions.models import Requisition
from procurer.supplyorders.models import SupplyOrder
from tests.api_tests import PassportMixin
from tests.fixture_manager import get_fixtures
from .settings import VIRUSTOTAL_SETTINGS, VIRUSTOTAL_TESTS_ENABLED


class VirusTotalSupplyChainTestCase(TransactionTestCase, PassportMixin):
    """
    Integration test for a SupplyOrder for VirusTotal.
    """

    allow_database_queries = True

    fixtures = get_fixtures(['supplyorders', 'quartermasters'])

    @classmethod
    def setUpClass(cls):
        super(VirusTotalSupplyChainTestCase, cls).setUpClass()

        # Start up celery worker
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        # Close worker
        cls.celery_worker.__exit__(None, None, None)
        super(VirusTotalSupplyChainTestCase, cls).tearDownClass()

    def setUp(self):
        super(VirusTotalSupplyChainTestCase, self).setUp()

        private_passport = Passport.objects.get_by_natural_key('VirusTotal Private')
        self._update_passport(private_passport, VIRUSTOTAL_SETTINGS)

        public_passport = Passport.objects.get_by_natural_key('VirusTotal Public')
        self._update_passport(public_passport, VIRUSTOTAL_SETTINGS)

    # @skipUnless(VIRUSTOTAL_TESTS_ENABLED, 'VirusTotal API tests disabled')
    # def test_process_request(self):
    #     """

    #     """
    #     self.maxDiff = None
    #     supply_order = SupplyOrder.objects.get(pk=1)
    #     supply_order = supply_order.process()

    #     actual_manifests = ([manifest.data for manifest in supply_order.manifests.all()])
    #     expected_manifests = [
    #         {
    #             'url': 'http://dunbararmored.com'
    #         }, {
    #             'resource': 'http://dunbararmored.com/'
    #         }
    #     ]
    #     self.assertEqual(actual_manifests, expected_manifests)

    #     expected_result = {
    #         'total': 67,
    #         '_platform': 'virustotal',
    #         '_distillery': 4,
    #         'url': 'http://dunbararmored.com/',
    #         'resource': 'http://dunbararmored.com/',
    #         'positives': 0,
    #         'filescan_id': None,
    #     }
    #     actual_result = supply_order.result
    #     for key in ['_id', '_saved_date', 'permalink', 'scan_date', 'scan_id']:
    #         actual_result.pop(key)
    #     self.assertEqual(actual_result, expected_result)


class VirusTotalTestCase(TestCase, PassportMixin):
    """
    Base class for VirusTotal tests.
    """

    fixtures = get_fixtures(['requisitions', 'quartermasters'])

    def setUp(self):
        super(VirusTotalTestCase, self).setUp()

        private_passport = Passport.objects.get_by_natural_key('VirusTotal Private')
        self._update_passport(private_passport, VIRUSTOTAL_SETTINGS)

        public_passport = Passport.objects.get_by_natural_key('VirusTotal Public')
        self._update_passport(public_passport, VIRUSTOTAL_SETTINGS)

    @skipUnless(VIRUSTOTAL_TESTS_ENABLED, 'VirusTotal API tests disabled')
    def test_url_report(self):
        """

        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'UrlReport')
        handler = UrlReport(endpoint)
        url = 'dunbararmored.com'

        cargo = handler.process_request({'resource': url})

        expected_data = 0
        actual_data = cargo.data['positives']
        self.assertEqual(actual_data, expected_data)

        expected_code = 1
        actual_code = cargo.status_code
        self.assertEqual(actual_code, expected_code)

        expected_notes = 'Scan finished, scan information embedded in this object'
        actual_notes = cargo.notes
        self.assertEqual(actual_notes, expected_notes)

    # @skipUnless(VIRUSTOTAL_TESTS_ENABLED, 'VirusTotal API tests disabled')
    # def test_url_scan(self):
    #     """

    #     """
    #     endpoint = Requisition.objects.get_by_natural_key('virustotal',
    #                                                       'UrlReport')
    #     handler = UrlScan(endpoint)
    #     url = 'dunbararmored.com'

    #     cargo = handler.process_request({'resource': url})
    #     print(cargo.data)
    #     expected_data = 0
    #     actual_data = cargo.data['positives']
    #     self.assertEqual(actual_data, expected_data)

    #     expected_code = 1
    #     actual_code = cargo.status_code
    #     self.assertEqual(actual_code, expected_code)

    #     expected_notes = 'Scan finished, scan information embedded in this object'
    #     actual_notes = cargo.notes
    #     self.assertEqual(actual_notes, expected_notes)


# class UrlScanSupplyChainTestCase(VirusTotalTestCase):
#     """
#     Tests the Url scan SupplyChain.
#     """

#     def test_process_request(self):
#         """

#         """
#         supplychain = SupplyChain.objects.get_by_natural_key('VirusTotal URL Scan & Report')
#         print('count', supplychain.supplylinks.count())
#         result = supplychain.start(user=None, data={'url': 'dunbararmored.com'})

#         print('result', result)
#         print('result code', result.status_code)
#         print('result notes', result.notes)
