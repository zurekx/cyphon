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
Defines classes for VirusTotal handlers.

==================================  ===========================================
Class                               Description
==================================  ===========================================
:class:`~VirusTotalHandler`         Base class for interacting with VirusTotal.
:class:`~VirusTotalResourceReport`  Base class for resource-related endpoints.
:class:`~DomainReport`              Accesses the endpoint for domain reports.
:class:`~FileReport`                Accesses the endpoint for file reports.
:class:`~FileScan`                  Accesses the endpoint for file scanning.
:class:`~IPAddressReport`           Accesses the endpoint for IP addr reports.
:class:`~RescanReport`              Accesses the endpoint for file rescanning.
:class:`~UrlReport`                 Accesses the endpoint for URL reports.
:class:`~UrlScan`                   Accesses the endpoint for URL scanning.
==================================  ===========================================

"""

# standard library
import os
import time
import urllib

# third party
import requests

# local
from ambassador.transport import Cargo
from cyphon.version import VERSION
from procurer.convoy import Convoy

_WAIT_TIME_SECONDS = 60
_RETRIES = 6


class VirusTotalHandler(Convoy):
    """Base class for interacting with VirusTotal APIs."""

    base_url = 'https://www.virustotal.com/vtapi/v2/'

    api = ''

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'gzip, Cyphon %s' % VERSION
    }

    wait_time_seconds = _WAIT_TIME_SECONDS

    retries = _RETRIES

    def __init__(self, *args, **kwargs):
        super(VirusTotalHandler, self).__init__(*args, **kwargs)
        self.url = self.base_url + self.api
        self.api_key = self.get_key()

    def _get_params(self):
        """Return a |dict| of credentials for VirusTotal authentication."""
        return {'apikey': self.api_key}

    def _update_params(self, obj, key):
        """Add a dictionary item to the VirusTotal request parameters.

        Takes a dictionary object and a key, and adds the corresponding
        item from the dictionary to the parameters dictionary.
        """
        params = self._get_params()
        params[key] = obj.get(key)
        return params

    def _get_url(self, params):
        """Add parameters to the URL and return the HTTP Response."""
        url = '%s?%s' % (self.url, urllib.urlencode(params))
        return urllib.urlopen(url).read()

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        raise NotImplementedError

    @staticmethod
    def _package_cargo(response):
        """Return a |Cargo| object based on a HTTP Response."""
        if response.status_code == 200:
            response_dict = response.json()
            status_code = response_dict.pop('response_code', '')
            verbose_msg = response_dict.pop('verbose_msg', '')
        else:
            response_dict = {}
            status_code = response.status_code
            verbose_msg = response.reason

        return Cargo(
            status_code=status_code,
            data=response_dict,
            notes=verbose_msg
        )

    def process_request(self, obj):
        """Process an API request and return a |Cargo| object for the response.

        Parameters
        ----------
        obj : |dict|
            A |dict| containing parameters for a VirusTotal API request.

        Returns
        -------
        |Cargo|
            The results of the API call to VirusTotal.

        """
        response = self._get_response(obj)
        return self._package_cargo(response)


class VirusTotalResourceReport(VirusTotalHandler):
    """Accesses the VirusTotal API endpoint for resource reports."""

    def _get_response(self, obj):
        """Take a dict of parameters and get the API response."""
        params = self._update_params(obj, 'resource')
        return requests.get(self.url, params=params, headers=self.headers)


class DomainReport(VirusTotalHandler):
    """Accesses the VirusTotal API endpoint for domain reports."""

    api = 'domain/report'

    def _get_response(self, obj):
        """Take a dict of parameters and get the API response."""
        params = self._update_params(obj, 'domain')
        return self._get_url(params)


class FileReport(VirusTotalResourceReport):
    """Accesses the VirusTotal API endpoint for file reports."""

    api = 'file/report'


class FileScan(VirusTotalHandler):
    """Accesses the VirusTotal API endpoint for file scanning.

    {
      'permalink': 'https://www.virustotal.com/file/d1...',
      'resource': u'd140c244ef892e59c7f68bd0c6f74bb711...',
      'response_code': 1,
      'scan_id': 'd140c244ef892e59c7f68bd0c6f74bb71103...',
      'verbose_msg': 'Scan request successfully queued...',
      'sha256': 'd140c244ef892e59c7f68bd0c6f74bb711032...'
    }

    """

    api = 'file/scan'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._get_params()
        file_path = obj.get('file')
        file_name = os.path.basename(file_path)
        files = {'file': (file_name, open(file_path, 'rb'))}
        return requests.post(self.url, files=files, params=params)


class IPAddressReport(VirusTotalHandler):
    """Accesses the VirusTotal API endpoint for IP address reports."""

    api = 'ip-address/report'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'url')
        return self._get_url(params)


class RescanReport(VirusTotalResourceReport):
    """Accesses the VirusTotal API endpoint for file rescanning."""

    api = 'file/rescan'


class UrlReport(VirusTotalResourceReport):
    """Accesses the VirusTotal API endpoint for URL reports."""

    api = 'url/report'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'resource')
        params.update({'scan': 1})  # submit for analysis if no report is found
        return requests.post(self.url, data=params)

    def _process_cargo(self, cargo, tries=0):
        """Take a |Cargo| object and use it submit another request if needed.

        Takes a |Cargo| object from a previous API call and performs
        additional operations if necessary.

        Parameters
        ----------
        cargo : |Cargo|
            The results of a previous API call to VirusTotal.

        tries : int
            The number of prior requests that have been made.

        Returns
        -------
        |Cargo|
            The final results.

        """
        if cargo.data and 'scans' not in cargo.data and \
                'scan_id' in cargo.data and tries <= self.retries:
            time.sleep(self.wait_time_seconds)
            cargo.data['resource'] = cargo.data['scan_id']
            response = self._get_response(cargo.data)
            cargo = self._package_cargo(response)
            tries += 1
            return self._process_cargo(cargo, tries)
        else:
            return cargo

    def process_request(self, obj):
        """Process an API request and return a |Cargo| object for the response.

        Parameters
        ----------
        obj : |dict|
            A |dict| containing parameters for an API request.

        Returns
        -------
        |Cargo|
            The results of the API call to VirusTotal.

        """
        response = self._get_response(obj)
        cargo = self._package_cargo(response)
        return self._process_cargo(cargo)


class UrlScan(VirusTotalHandler):
    """Accesses the VirusTotal API endpoint for URL scanning."""

    api = 'url/scan'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'url')
        return requests.post(self.url, data=params)
