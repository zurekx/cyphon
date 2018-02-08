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
import time
from unittest import skipUnless

# third party
from celery.contrib.testing.worker import start_worker
from django.test import TestCase, TransactionTestCase

# local
from ambassador.passports.models import Passport
from cyphon.celeryapp import app
from platforms.virustotal.handlers import (
    FileReport,
    FileScan,
    IPAddressReport,
    RescanReport,
    UrlReport,
    UrlScan
)
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

    @skipUnless(VIRUSTOTAL_TESTS_ENABLED, 'VirusTotal API tests disabled')
    def test_process_request(self):
        """

        """
        self.maxDiff = None
        supply_order = SupplyOrder.objects.get(pk=1)
        supply_order = supply_order.process()

        actual_manifests = ([manifest.data for manifest in supply_order.manifests.all()])
        expected_manifests = [
            {
                'url': 'http://dunbararmored.com'
            }, {
                'resource': 'http://dunbararmored.com/'
            }
        ]
        self.assertEqual(actual_manifests, expected_manifests)

        expected_result = {
            'total': 67,
            '_platform': 'virustotal',
            '_distillery': 4,
            'url': 'http://dunbararmored.com/',
            'resource': 'http://dunbararmored.com/',
            'positives': 0,
            'filescan_id': None,
        }
        actual_result = supply_order.result
        for key in ['_id', '_saved_date', 'permalink', 'scan_date', 'scan_id']:
            actual_result.pop(key)
        self.assertEqual(actual_result, expected_result)


@skipUnless(VIRUSTOTAL_TESTS_ENABLED, 'VirusTotal API tests disabled')
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

        time.sleep(15)  # VirusTotal API only allows 4 calls per min

    def test_domain_report(self):
        """
        Tests the DomainReport handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'DomainReport')
        handler = UrlScan(endpoint)
        url = 'www.virustotal.com/'

        cargo = handler.process_request({'url': url})

        resource = 'http://www.virustotal.com/'
        verbose_msg = ('Scan request successfully queued, come back later '
                       'for the report')

        self.assertEqual(cargo.data['resource'], resource)
        self.assertEqual(cargo.notes, verbose_msg)
        self.assertEqual(cargo.status_code, 1)

    def test_file_report(self):
        """
        Tests the FileReport handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'FileReport')
        handler = FileReport(endpoint)
        resource = ('f22aa73c0177d4405631128783bd1e4adf47d8925dfc62775f'
                    '213c4bbaa13d35')

        cargo = handler.process_request({'resource': resource})

        verbose_msg = 'Scan finished, information embedded'

        self.assertEqual(cargo.data['resource'], resource)
        self.assertEqual(cargo.notes, verbose_msg)
        self.assertEqual(cargo.status_code, 1)

    def test_file_scan(self):
        """
        Tests the FileScan handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'FileScan')
        handler = FileScan(endpoint)
        file_path = __file__

        cargo = handler.process_request({'file': file_path})

        verbose_msg = ('Scan request successfully queued, come back later '
                       'for the report')

        self.assertEqual(cargo.notes, verbose_msg)
        self.assertEqual(cargo.status_code, 1)

    def test_ipaddr_report(self):
        """
        Tests the IPAddressReport handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'IPAddressReport')
        handler = IPAddressReport(endpoint)
        resource = '216.239.32.21'

        cargo = handler.process_request({'ip': resource})

        verbose_msg = 'IP address in dataset'

        self.assertEqual(cargo.notes, verbose_msg)
        self.assertEqual(cargo.status_code, 1)

    def test_rescan_report(self):
        """
        Tests the RescanReport handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'RescanReport')
        handler = RescanReport(endpoint)
        resource = ('6171d125c1d8d9b6e1706bf8a418282e89b36ae844a2c53407d'
                    'bcd237320e2c9')

        cargo = handler.process_request({'resource': resource})

        permalink = ('https://www.virustotal.com/file/6171d125c1d8d9b6e'
                     '1706bf8a418282e89b36ae844a2c53407dbcd237320e2c9/'
                     'analysis/1517860508/')

        self.assertEqual(cargo.data['resource'], resource)
        self.assertEqual(cargo.data['sha256'], resource)
        self.assertEqual(cargo.notes, '')
        self.assertEqual(cargo.status_code, 1)

    def test_url_report(self):
        """
        Tests the URLReport handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'UrlReport')
        handler = UrlReport(endpoint)
        url = 'www.virustotal.com'

        cargo = handler.process_request({'resource': url})

        expected_data = 0
        actual_data = cargo.data['positives']
        self.assertEqual(actual_data, expected_data)

        expected_code = 1
        actual_code = cargo.status_code
        self.assertEqual(actual_code, expected_code)

        expected_notes = ('Scan finished, scan information embedded '
                          'in this object')
        actual_notes = cargo.notes
        self.assertEqual(actual_notes, expected_notes)

    def test_url_scan(self):
        """
        Tests the URLScan handler.
        """
        endpoint = Requisition.objects.get_by_natural_key('virustotal',
                                                          'UrlScan')
        handler = UrlScan(endpoint)
        url = 'www.virustotal.com'

        cargo = handler.process_request({'url': url})

        resource = 'http://www.virustotal.com/'
        verbose_msg = ('Scan request successfully queued, come back later '
                       'for the report')

        self.assertEqual(cargo.data['resource'], resource)
        self.assertEqual(cargo.notes, verbose_msg)
        self.assertEqual(cargo.status_code, 1)
