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

from keystoneclient import session as ks_session
import mock

from ceilometerclient import client
from ceilometerclient.tests import fakes
from ceilometerclient.tests import utils
from ceilometerclient.v1 import client as v1client
from ceilometerclient.v2 import client as v2client

FAKE_ENV = {
    'username': 'username',
    'password': 'password',
    'tenant_name': 'tenant_name',
    'auth_url': 'http://no.where',
    'ceilometer_url': 'http://no.where',
    'auth_plugin': 'fake_auth',
    'token': '1234',
    'user_domain_name': 'default',
    'project_domain_name': 'default',
}


class ClientTest(utils.BaseTestCase):

    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)

        return client.get_client(api_version, **env)

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

    def test_client_without_auth_plugin_keystone_v3(self):
        env = FAKE_ENV.copy()
        del env['auth_plugin']
        expected = {
            'username': 'username',
            'endpoint': 'http://no.where',
            'tenant_name': 'tenant_name',
            'service_type': None,
            'token': '1234',
            'endpoint_type': None,
            'region_name': None,
            'auth_url': 'http://no.where',
            'tenant_id': None,
            'insecure': None,
            'cacert': None,
            'password': 'password',
            'user_domain_name': 'default',
            'user_domain_id': None,
            'project_domain_name': 'default',
            'project_domain_id': None,
        }
        with mock.patch('ceilometerclient.client.AuthPlugin') as auth_plugin:
            self.create_client(env, api_version=2, endpoint='http://no.where')
            auth_plugin.assert_called_with(**expected)

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
            'verify': True,
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

    @mock.patch.object(ks_session, 'Session')
    def test_v2_client_timeout_keystone_seesion(self, mocked_session):
        mocked_session.side_effect = RuntimeError('Stop!')
        env = FAKE_ENV.copy()
        env['timeout'] = 5
        del env['auth_plugin']
        del env['token']
        client = self.create_client(env)
        self.assertRaises(RuntimeError, client.alarms.list)
        args, kwargs = mocked_session.call_args
        self.assertEqual(5, kwargs['timeout'])

    def test_v2_client_cacert_in_verify(self):
        env = FAKE_ENV.copy()
        env['cacert'] = '/path/to/cacert'
        client = self.create_client(env)
        self.assertEqual('/path/to/cacert', client.client.verify)

    def test_v2_client_certfile_and_keyfile(self):
        env = FAKE_ENV.copy()
        env['cert_file'] = '/path/to/cert'
        env['key_file'] = '/path/to/keycert'
        client = self.create_client(env)
        self.assertEqual(('/path/to/cert', '/path/to/keycert'),
                         client.client.cert)

    def test_v2_client_insecure(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin')
        env['insecure'] = 'True'
        client = self.create_client(env)
        self.assertIn('insecure', client.auth_plugin.opts)
        self.assertEqual('True', client.auth_plugin.opts['insecure'])


class ClientTest2(ClientTest):
    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)

        # Run the same tests with direct instantiation of the Client
        return client.Client(api_version, endpoint, **env)
