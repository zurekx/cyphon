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
Defines classes for JIRA actions.
"""

# standard library
import json
import os
import urllib

# third party
import requests

# local
from ambassador.transport import Cargo
from cyphon.version import VERSION
from procurer.convoy import Convoy


class VirusTotalHandler(Convoy):
    """
    Base class for interacting with JIRA APIs.
    """

    base_url = 'https://www.virustotal.com/vtapi/v2/'

    api = ''

    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'gzip, Cyphon %s' % VERSION
    }

    def __init__(self, *args, **kwargs):
        super(VirusTotalHandler, self).__init__(*args, **kwargs)
        self.url = self.base_url + self.api
        self.api_key = self.get_key()

    def _get_params(self):
        """
        Returns a dictionary of credentials for VirusTotal authentication.
        """
        return {'apikey': self.api_key}

    def _update_params(self, obj, key):
        """
        Returns a dictionary of credentials for VirusTotal authentication.
        """
        params = self._get_params()
        params[key] = obj.get(key)
        return params

    def _get_url(self, params):
        """

        """
        url = '%s?%s' % (self.url, urllib.urlencode(params))
        return urllib.urlopen(url).read()

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        raise NotImplementedError

    @staticmethod
    def _package_cargo(response):
        """

        """
        response_dict = json.loads(response)
        status_code = response_dict.pop('response_code')
        verbose_msg = response_dict.pop('verbose_msg')

        return Cargo(
            status_code=status_code,
            data=response_dict,
            notes=verbose_msg
        )

    def process_request(self, obj):
        """

        Parameters
        ----------
        obj : |dict|
            The |dict| containing a 'resource' dictionary key.

        Returns
        -------
        |Cargo|
            The results of the API call to VirusTotal.

        """
        response = self._get_response(obj)
        return self._package_cargo(response)


class VirusTotalResourceReport(VirusTotalHandler):
    """
    Class for accessing the VirusTotal API endpoint for resource reports.
    """

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'resource')
        return requests.get(self.url, params=params, headers=self.headers)


class FileScan(VirusTotalHandler):
    """
    Class for accessing the VirusTotal API endpoint for file scanning.

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


class FileReport(VirusTotalResourceReport):
    """
    Class for accessing the VirusTotal API endpoint for file reports.
    """

    api = 'file/report'


class RescanReport(VirusTotalResourceReport):
    """
    Class for accessing the VirusTotal API endpoint for file rescanning.
    """

    api = 'file/rescan'


class UrlScan(VirusTotalHandler):
    """
    Class for accessing the VirusTotal API endpoint for URL scanning.
    """

    api = 'url/scan'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'url')
        return requests.post(self.url, data=params)


class UrlReport(VirusTotalResourceReport):
    """
    Class for accessing the VirusTotal API endpoint for URL reporst.
    """

    api = 'url/report'


class IPAddressReport(VirusTotalHandler):
    """
    Class for accessing the VirusTotal API endpoint for IP address reports.
    """

    api = 'ip-address/report'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'url')
        return self._get_url(params)


class DomainReport(VirusTotalHandler):
    """
    Class for accessing the VirusTotal API endpoint for domain reports.
    """

    api = 'domain/report'

    def _get_response(self, obj):
        """Take a dict or parameters and get the API response."""
        params = self._update_params(obj, 'domain')
        return self._get_url(params)
