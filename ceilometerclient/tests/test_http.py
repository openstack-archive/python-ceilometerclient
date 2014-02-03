# Copyright 2012 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib
import mock

from ceilometerclient.common import http
from ceilometerclient.tests import utils


class HttpClientTest(utils.BaseTestCase):
    url = 'http://localhost'

    def test_url_generation_trailing_slash_in_base(self):
        client = http.HTTPClient("%s/" % self.url)
        url = client._make_connection_url('/v1/resources')
        self.assertEqual(url, '/v1/resources')

    def test_url_generation_without_trailing_slash_in_base(self):
        client = http.HTTPClient(self.url)
        url = client._make_connection_url('/v1/resources')
        self.assertEqual(url, '/v1/resources')

    def test_url_generation_prefix_slash_in_path(self):
        client = http.HTTPClient("%s/" % self.url)
        url = client._make_connection_url('/v1/resources')
        self.assertEqual(url, '/v1/resources')

    def test_url_generation_without_prefix_slash_in_path(self):
        client = http.HTTPClient(self.url)
        url = client._make_connection_url('v1/resources')
        self.assertEqual(url, '/v1/resources')

    def test_get_connection(self):
        client = http.HTTPClient(self.url)
        self.assertIsNotNone(client.get_connection())

    def test_url_generation_with_proxy(self):
        client = http.HTTPClient(self.url)
        client.proxy_url = "http://localhost:3128/"
        conn = mock.MagicMock()
        with contextlib.nested(
            mock.patch.object(client, 'get_connection'),
            mock.patch.object(client, 'auth_token')
        ) as (get_conn, auth_token):
            conn.request.side_effect = Exception("stop")
            get_conn.return_value = conn
            auth_token.return_value = "token"
            try:
                client._http_request('/v1/resources', 'GET')
            except Exception:
                pass
        conn.request.assert_called_once_with('GET', (self.url.rstrip('/') +
                                                     '/v1/resources'),
                                             headers=mock.ANY)


class HttpsClientTest(HttpClientTest):
    url = 'https://localhost'


class HttpEndingSlashClientTest(HttpClientTest):
    url = 'http://localhost/'
