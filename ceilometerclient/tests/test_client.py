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

import mock

from ceilometerclient import client
from ceilometerclient.tests import fakes
from ceilometerclient.tests import utils
from ceilometerclient.v1 import client as v1client
from ceilometerclient.v2 import client as v2client

FAKE_ENV = {'username': 'username',
            'password': 'password',
            'tenant_name': 'tenant_name',
            'auth_url': 'http://no.where',
            'ceilometer_url': 'http://no.where',
            'auth_plugin': 'fake_auth',
            'token': '1234'}


class ClientTest(utils.BaseTestCase):

    def create_client(self, env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)

        return client.Client(api_version, endpoint, **env)

    def setUp(self):
        super(ClientTest, self).setUp()

    def test_client_version(self):
        c1 = self.create_client(env=FAKE_ENV, api_version=1)
        self.assertIsInstance(c1, v1client.Client)

        c2 = self.create_client(env=FAKE_ENV, api_version=2)
        self.assertIsInstance(c2, v2client.Client)

    def test_client_auth_lambda(self):
        env = FAKE_ENV.copy()
        env['token'] = lambda: env['token']
        self.assertIsInstance(env['token'],
                              types.FunctionType)
        c2 = self.create_client(env)
        self.assertIsInstance(c2, v2client.Client)

    def test_client_auth_non_lambda(self):
        env = FAKE_ENV.copy()
        env['token'] = "1234"
        self.assertIsInstance(env['token'], str)
        c2 = self.create_client(env)
        self.assertIsInstance(c2, v2client.Client)

    @mock.patch('keystoneclient.v2_0.client', fakes.FakeKeystone)
    def test_client_without_auth_plugin(self):
        env = FAKE_ENV.copy()
        del env['auth_plugin']
        c = self.create_client(env, api_version=2, endpoint='fake_endpoint')
        self.assertIsInstance(c.auth_plugin, client.AuthPlugin)

    def test_client_with_auth_plugin(self):
        c = self.create_client(FAKE_ENV, api_version=2)
        self.assertIsInstance(c.auth_plugin, str)

    def test_v2_client_timeout_invalid_value(self):
        env = FAKE_ENV.copy()
        env['timeout'] = 'abc'
        self.assertRaises(ValueError, self.create_client, env)
        env['timeout'] = '1.5'
        self.assertRaises(ValueError, self.create_client, env)

    def _test_v2_client_timeout_integer(self, timeout, expected_value):
        env = FAKE_ENV.copy()
        env['timeout'] = timeout
        expected = {
            'auth_plugin': 'fake_auth',
            'timeout': expected_value,
            'original_ip': None,
            'http': None,
            'region_name': None,
            'verify': None,
            'timings': None,
            'keyring_saver': None,
            'cert': None,
            'endpoint_type': None,
            'user_agent': None,
            'debug': None,
        }
        cls = 'ceilometerclient.openstack.common.apiclient.client.HTTPClient'
        with mock.patch(cls) as mocked:
            self.create_client(env)
            mocked.assert_called_with(**expected)

    def test_v2_client_timeout_zero(self):
        self._test_v2_client_timeout_integer(0, None)

    def test_v2_client_timeout_valid_value(self):
        self._test_v2_client_timeout_integer(30, 30)
