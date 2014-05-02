#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import types

from ceilometerclient import client
from ceilometerclient.tests import utils
from ceilometerclient.v1 import client as v1client
from ceilometerclient.v2 import client as v2client

FAKE_ENV = {'os_username': 'username',
            'os_password': 'password',
            'os_tenant_name': 'tenant_name',
            'os_auth_url': 'http://no.where',
            'os_auth_token': '1234',
            'ceilometer_url': 'http://no.where'}


class ClientTest(utils.BaseTestCase):

    def create_client(self, api_version=2, exclude=[]):
        env = dict((k, v) for k, v in FAKE_ENV.items() if k not in exclude)
        return client.get_client(api_version, **env)

    def setUp(self):
        super(ClientTest, self).setUp()

    def test_client_version(self):
        c1 = self.create_client(api_version=1)
        self.assertIsInstance(c1, v1client.Client)

        c2 = self.create_client(api_version=2)
        self.assertIsInstance(c2, v2client.Client)

    def test_client_auth_token_lambda(self):
        FAKE_ENV['os_auth_token'] = lambda: '1234'
        self._test_client_auth_token()

    def test_client_auth_token_non_lambda(self):
        FAKE_ENV['os_auth_token'] = "1234"
        self._test_client_auth_token()

    def _test_client_auth_token(self):
        c2 = self.create_client()
        self.assertIsInstance(c2, v2client.Client)
        self.assertIsInstance(c2.http_client.auth_token,
                              types.FunctionType)
        self.assertEqual('1234', c2.http_client.auth_token())
