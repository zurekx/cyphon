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

# standard library
# try:
#     from unittest.mock import Mock, patch
# except ImportError:
#     from mock import Mock, patch

# standard library
from unittest import skipUnless

# third party
from celery.contrib.testing.worker import start_worker
from django.test import SimpleTestCase, TestCase, TransactionTestCase
from rest_framework.test import APISimpleTestCase

# local
from cyphon.celeryapp import app
from platforms.tests.test_apihandler import PassportMixin
from platforms.virustotal.handlers import UrlReport
from procurer.requisitions.models import Requisition
from procurer.supplychains.models import SupplyChain
from procurer.supplyorders.models import SupplyOrder
from tests.fixture_manager import get_fixtures
from .settings import VIRUSTOTAL_SETTINGS, VIRUSTOTAL_TESTS_ENABLED


class UrlScanSupplyChainTestCase(TransactionTestCase, PassportMixin):
    """

    """

    allow_database_queries = True

    fixtures = get_fixtures(['supplyorders', 'quartermasters'])
    # fixtures = get_fixtures(['virustotal'])

    @classmethod
    def setUpClass(cls):
        super(UrlScanSupplyChainTestCase, cls).setUpClass()
        # Start up celery worker
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super(UrlScanSupplyChainTestCase, cls).tearDownClass()

        # Close worker
        cls.celery_worker.__exit__(None, None, None)

    @skipUnless(VIRUSTOTAL_TESTS_ENABLED, 'VirusTotal API tests disabled')
    def test_process_request(self):
        """

        """
        supply_chain = SupplyChain.objects.get_by_natural_key('VirusTotal URL Scan & Report')
        supply_order = SupplyOrder.objects.get(pk=1)
        result = supply_order.process()
        # result = supply_chain.start(data={'url': 'dunbararmored.com'}, supply_order=supply_order)
        print([(manifest.data, manifest.status_code, manifest.response_msg) for manifest in supply_order.manifests.all()])
        # [({'url': 'http://example.com'}, '403', 'Forbidden'), ({'resource': None}, '403', 'Forbidden')]

# class UrlReportTestCase(TestCase):
#     """
#     Tests the UrlReport class.
#     """

#     fixtures = get_fixtures(['virustotal'])

#     def test_process_request(self):
#         """

#         """
#         endpoint = Requisition.objects.get_by_natural_key('virustotal',
#                                                           'UrlReport')
#         handler = UrlReport(endpoint)
#         url = 'dunbafhjfgfrahfsdhrdfdmored.com'

#         cargo = handler.process_request({'resource': url})
#         print('data', cargo.data)
#         print('code', cargo.status_code)
#         print('notes', cargo.notes)


# class UrlScanSupplyChainTestCase(TestCase):
#     """
#     Tests the Url scan SupplyChain.
#     """

#     fixtures = get_fixtures(['virustotal'])

#     def test_process_request(self):
#         """

#         """
#         supplychain = SupplyChain.objects.get_by_natural_key('VirusTotal URL Scan & Report')
#         print('count', supplychain.supplylinks.count())
#         result = supplychain.start(user=None, data={'url': 'dunbararmored.com'})

#         print('result', result)
#         # print('result code', result.status_code)
#         # print('result notes', result.notes)
