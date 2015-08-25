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

from keystoneclient.auth.identity import v2 as v2_auth
from keystoneclient.auth.identity import v3 as v3_auth
from keystoneclient import exceptions as ks_exc
from keystoneclient import session as ks_session
import mock

from ceilometerclient import client
from ceilometerclient import exc
from ceilometerclient.openstack.common.apiclient import exceptions
from ceilometerclient.tests.unit import fakes
from ceilometerclient.tests.unit import utils
from ceilometerclient.v1 import client as v1client
from ceilometerclient.v2 import client as v2client

FAKE_ENV = {
    'username': 'username',
    'password': 'password',
    'tenant_name': 'tenant_name',
    'auth_url': 'http://no.where',
    'auth_plugin': mock.Mock(),
    'ceilometer_url': 'http://no.where',
    'token': '1234',
    'user_domain_name': 'default',
    'project_domain_name': 'default',
}


class ClientTest(utils.BaseTestCase):
    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)
        if not env.get('auth_plugin'):
            with mock.patch('ceilometerclient.client.AuthPlugin.'
                            'redirect_to_aodh_endpoint') as redirect_aodh:
                redirect_aodh.side_effect = ks_exc.EndpointNotFound
                return client.get_client(api_version, **env)
        else:
            env['auth_plugin'].redirect_to_aodh_endpoint.side_effect = \
                ks_exc.EndpointNotFound
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
            'auth_plugin': mock.ANY,
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
        if not env.get('auth_plugin'):
            with mock.patch('ceilometerclient.client.AuthPlugin.'
                            'redirect_to_aodh_endpoint') as redirect_aodh:
                redirect_aodh.side_effect = ks_exc.EndpointNotFound
                return client.Client(api_version, endpoint, **env)
        else:
            env['auth_plugin'].redirect_to_aodh_endpoint.side_effect = \
                ks_exc.EndpointNotFound
            return client.Client(api_version, endpoint, **env)


class ClientTestWithAodh(ClientTest):
    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)
        if not env.get('auth_plugin'):
            with mock.patch('ceilometerclient.client.AuthPlugin.'
                            'redirect_to_aodh_endpoint'):
                return client.get_client(api_version, **env)
        else:
            env['auth_plugin'].redirect_to_aodh_endpoint = mock.MagicMock()
            return client.get_client(api_version, **env)

    @mock.patch('keystoneclient.v2_0.client', fakes.FakeKeystone)
    def test_client_without_auth_plugin(self):
        env = FAKE_ENV.copy()
        del env['auth_plugin']
        c = self.create_client(env, api_version=2, endpoint='fake_endpoint')
        self.assertIsInstance(c.alarm_auth_plugin, client.AuthPlugin)

    def test_v2_client_insecure(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin')
        env['insecure'] = 'True'
        client = self.create_client(env)
        self.assertIn('insecure', client.alarm_auth_plugin.opts)
        self.assertEqual('True', client.alarm_auth_plugin.opts['insecure'])


class ClientAuthTest(utils.BaseTestCase):

    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)

        return client.get_client(api_version, **env)

    @mock.patch('keystoneclient.discover.Discover')
    @mock.patch('keystoneclient.session.Session')
    def test_discover_auth_versions(self, session, discover_mock):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)

        mock_session_instance = mock.MagicMock()
        session.return_value = mock_session_instance

        client = self.create_client(env)
        client.auth_plugin.opts.pop('token', None)
        client.auth_plugin._do_authenticate(mock.MagicMock())

        self.assertEqual([mock.call(auth_url='http://no.where',
                                    session=mock_session_instance),
                          mock.call(auth_url='http://no.where',
                                    session=mock_session_instance)],
                         discover_mock.call_args_list)
        self.assertIsInstance(mock_session_instance.auth, v3_auth.Password)

    @mock.patch('keystoneclient.discover.Discover')
    @mock.patch('keystoneclient.session.Session')
    def test_discover_auth_versions_v2_only(self, session, discover):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('user_domain_name', None)
        env.pop('user_domain_id', None)
        env.pop('project_domain_name', None)
        env.pop('project_domain_id', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        discover_instance_mock = mock.MagicMock()
        discover_instance_mock.url_for.side_effect = (lambda v: v
                                                      if v == '2.0' else None)
        discover.return_value = discover_instance_mock

        client = self.create_client(env)
        client.auth_plugin.opts.pop('token', None)
        client.auth_plugin._do_authenticate(mock.MagicMock())
        self.assertEqual([mock.call(auth_url='http://no.where',
                                    session=session_instance_mock),
                          mock.call(auth_url='http://no.where',
                                    session=session_instance_mock)],
                         discover.call_args_list)

        self.assertIsInstance(session_instance_mock.auth, v2_auth.Password)

    @mock.patch('keystoneclient.discover.Discover')
    @mock.patch('keystoneclient.session.Session')
    def test_discover_auth_versions_raise_discovery_failure(self,
                                                            session,
                                                            discover):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        discover_instance_mock = mock.MagicMock()
        discover_instance_mock.url_for.side_effect = (lambda v: v
                                                      if v == '2.0' else None)
        discover.side_effect = ks_exc.DiscoveryFailure
        self.assertRaises(ks_exc.DiscoveryFailure, self.create_client, env)
        discover.side_effect = mock.MagicMock()
        client = self.create_client(env)
        discover.side_effect = ks_exc.DiscoveryFailure
        client.auth_plugin.opts.pop('token', None)

        self.assertRaises(ks_exc.DiscoveryFailure,
                          client.auth_plugin._do_authenticate,
                          mock.Mock())
        self.assertEqual([mock.call(auth_url='http://no.where',
                                    session=session_instance_mock),
                          mock.call(auth_url='http://no.where',
                                    session=session_instance_mock),
                          mock.call(auth_url='http://no.where',
                                    session=session_instance_mock)],
                         discover.call_args_list)

    @mock.patch('keystoneclient.discover.Discover')
    @mock.patch('keystoneclient.session.Session')
    def test_discover_auth_versions_raise_command_err(self, session, discover):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        discover.side_effect = exceptions.ClientException

        # the redirect_to_aodh_endpoint method will raise CommandError if
        # didn't specify keystone api version
        self.assertRaises(exc.CommandError, self.create_client, env)
        with mock.patch('ceilomet'
                        'erclient.client.AuthPlugin.'
                        'redirect_to_aodh_endpoint'):
            client = self.create_client(env)
        client.auth_plugin.opts.pop('token', None)

        self.assertRaises(exc.CommandError,
                          client.auth_plugin._do_authenticate,
                          mock.Mock())

    @mock.patch('ceilometerclient.client._get_keystone_session')
    @mock.patch('ceilometerclient.client._get_token_auth_ks_session')
    def test_get_endpoint(self, token_session, session):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock
        token_ks_session_mock = mock.MagicMock()
        token_session.return_value = token_ks_session_mock

        client = self.create_client(env)
        token_ks_session_mock.get_endpoint.assert_called_with(
            interface='publicURL', region_name=None, service_type='alarming')
        client.auth_plugin.opts.pop('token', None)
        client.auth_plugin.opts.pop('endpoint')
        client.auth_plugin._do_authenticate(mock.MagicMock())
        session_instance_mock.get_endpoint.assert_called_with(
            region_name=None, interface='publicURL', service_type='metering')

    @mock.patch('ceilometerclient.client._get_token_auth_ks_session')
    def test_get_aodh_endpoint(self, session):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        self.create_client(env)
        session_instance_mock.get_endpoint.assert_called_with(
            region_name=None, interface='publicURL', service_type='alarming')

    def test_get_aodh_endpoint_without_auth_url(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)
        env.pop('auth_url', None)
        client = self.create_client(env, endpoint='fake_endpoint')
        self.assertEqual(client.alarm_auth_plugin.opts,
                         client.auth_plugin.opts)

    @mock.patch('ceilometerclient.client._get_keystone_session')
    @mock.patch('ceilometerclient.client._get_token_auth_ks_session')
    def test_get_different_endpoint_type(self, token_session, session):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)
        env['endpoint_type'] = 'internal'

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock
        token_ks_session_mock = mock.MagicMock()
        token_session.return_value = token_ks_session_mock

        client = self.create_client(env)
        token_ks_session_mock.get_endpoint.assert_called_with(
            interface='internal', region_name=None, service_type='alarming')
        client.auth_plugin.opts.pop('token', None)
        client.auth_plugin.opts.pop('endpoint')
        client.auth_plugin._do_authenticate(mock.MagicMock())
        session_instance_mock.get_endpoint.assert_called_with(
            region_name=None, interface='internal', service_type='metering')

    @mock.patch('ceilometerclient.client._get_keystone_session')
    @mock.patch('ceilometerclient.client._get_token_auth_ks_session')
    def test_get_sufficient_options_missing(self, token_session, session):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('password', None)
        env.pop('endpoint', None)
        env.pop('auth_token', None)
        env.pop('tenant_name', None)
        env.pop('username', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock
        client = self.create_client(env)
        client.auth_plugin.opts.pop('endpoint', None)
        self.assertRaises(exceptions.AuthPluginOptionsMissing,
                          client.auth_plugin.sufficient_options)
