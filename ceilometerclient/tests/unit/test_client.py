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

from keystoneauth1 import exceptions as ks_exc
from keystoneauth1.identity import v2 as v2_auth
from keystoneauth1.identity import v3 as v3_auth
from keystoneauth1 import session as ks_session
import mock
import requests

from ceilometerclient.apiclient import exceptions
from ceilometerclient import client
from ceilometerclient import exc
from ceilometerclient.tests.unit import utils
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
        with mock.patch(
                'ceilometerclient.v2.client.Client._get_redirect_client',
                return_value=None):
            return client.get_client(api_version, **env)

    def test_client_v2_with_session(self):
        resp = mock.Mock(status_code=200, text=b'')
        resp.json.return_value = []
        session = mock.Mock()
        session.request.return_value = resp
        c = client.get_client(2, session=session)
        c.resources.list()
        self.assertTrue(session.request.called)
        self.assertTrue(resp.json.called)

    def test_client_version(self):
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
            self.assertEqual(mock.call(**expected),
                             auth_plugin.mock_calls[0])

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
        cls = 'ceilometerclient.apiclient.client.HTTPClient'
        with mock.patch(cls) as mocked:
            self.create_client(env)
            mocked.assert_called_with(**expected)

    def test_v2_client_timeout_zero(self):
        self._test_v2_client_timeout_integer(0, None)

    def test_v2_client_timeout_valid_value(self):
        self._test_v2_client_timeout_integer(30, 30)

    @mock.patch.object(ks_session, 'Session')
    def test_v2_client_timeout_keystone_session(self, mocked_session):
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
        self.assertEqual('/path/to/cacert',
                         client.http_client.http_client.verify)

    def test_v2_client_certfile_and_keyfile(self):
        env = FAKE_ENV.copy()
        env['cert_file'] = '/path/to/cert'
        env['key_file'] = '/path/to/keycert'
        client = self.create_client(env)
        self.assertEqual(('/path/to/cert', '/path/to/keycert'),
                         client.http_client.http_client.cert)

    def test_v2_client_insecure(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin')
        env['os_insecure'] = 'True'
        client = self.create_client(env)
        self.assertIn('insecure', client.auth_plugin.opts)
        self.assertEqual('True', client.auth_plugin.opts['insecure'])


class ClientTest2(ClientTest):
    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)
        with mock.patch(
                'ceilometerclient.v2.client.Client._get_redirect_client',
                return_value=None):
            return client.Client(api_version, endpoint, **env)


class ClientTestWithAodh(ClientTest):
    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)
        with mock.patch('ceilometerclient.apiclient.client.'
                        'HTTPClient.client_request',
                        return_value=mock.MagicMock()):
            return client.get_client(api_version, **env)

    def test_client_without_auth_plugin(self):
        env = FAKE_ENV.copy()
        del env['auth_plugin']
        c = self.create_client(env, api_version=2, endpoint='fake_endpoint')
        self.assertIsInstance(c.alarm_client.http_client.auth_plugin,
                              client.AuthPlugin)

    def test_v2_client_insecure(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin')
        env['insecure'] = 'True'
        client = self.create_client(env)
        self.assertIn('insecure',
                      client.alarm_client.http_client.auth_plugin.opts)
        self.assertEqual('True', (client.alarm_client.http_client.
                                  auth_plugin.opts['insecure']))

    def test_ceilometerclient_available_without_aodh_services_running(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        with mock.patch('ceilometerclient.apiclient.client.'
                        'HTTPClient.client_request') as mocked_request:
            mocked_request.side_effect = requests.exceptions.ConnectionError
            ceiloclient = client.get_client(2, **env)
            self.assertIsInstance(ceiloclient, v2client.Client)

    @mock.patch('ceilometerclient.client.SessionClient')
    def test_http_client_with_session_and_aodh(self, mock_sc):
        session = mock.Mock()
        kwargs = {"session": session,
                  "service_type": "metering",
                  "user_agent": "python-ceilometerclient"}
        expected = {
            "auth": None,
            "interface": 'publicURL',
            "region_name": None,
            "timings": None,
            "session": session,
            "service_type": "metering",
            "user_agent": "python-ceilometerclient"}
        kwargs['aodh_endpoint'] = 'http://aodh.where'
        client._construct_http_client(**kwargs)
        mock_sc.assert_called_with(**expected)


class ClientAuthTest(utils.BaseTestCase):

    @staticmethod
    def create_client(env, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in env.items()
                   if k not in exclude)
        with mock.patch('ceilometerclient.apiclient.client.'
                        'HTTPClient.client_request',
                        return_value=mock.MagicMock()):
            return client.get_client(api_version, **env)

    @mock.patch('keystoneauth1.discover.Discover')
    @mock.patch('keystoneauth1.session.Session')
    def test_discover_auth_versions(self, session, discover_mock):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)

        mock_session_instance = mock.MagicMock()
        session.return_value = mock_session_instance

        client = self.create_client(env)
        client.auth_plugin.opts.pop('token', None)
        client.auth_plugin._do_authenticate(mock.MagicMock())

        self.assertEqual([mock.call(url='http://no.where',
                                    session=mock_session_instance)],
                         discover_mock.call_args_list)
        self.assertIsInstance(mock_session_instance.auth, v3_auth.Password)

    @mock.patch('keystoneauth1.discover.Discover')
    @mock.patch('keystoneauth1.session.Session')
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
        self.assertEqual([mock.call(url='http://no.where',
                                    session=session_instance_mock)],
                         discover.call_args_list)

        self.assertIsInstance(session_instance_mock.auth, v2_auth.Password)

    @mock.patch('keystoneauth1.discover.Discover')
    @mock.patch('keystoneauth1.session.Session')
    def test_discover_auth_versions_raise_discovery_failure(self,
                                                            session,
                                                            discover):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('token', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        discover_instance_mock = mock.MagicMock()
        discover_instance_mock.url_for.side_effect = (lambda v: v
                                                      if v == '2.0' else None)
        discover.side_effect = ks_exc.DiscoveryFailure
        client = self.create_client(env)
        self.assertRaises(ks_exc.DiscoveryFailure,
                          client.auth_plugin._do_authenticate,
                          mock.Mock())
        discover.side_effect = mock.MagicMock()
        client = self.create_client(env)
        discover.side_effect = ks_exc.DiscoveryFailure
        client.auth_plugin.opts.pop('token', None)

        self.assertRaises(ks_exc.DiscoveryFailure,
                          client.auth_plugin._do_authenticate,
                          mock.Mock())
        self.assertEqual([mock.call(url='http://no.where',
                                    session=session_instance_mock),
                          mock.call(url='http://no.where',
                                    session=session_instance_mock)],
                         discover.call_args_list)

    @mock.patch('ceilometerclient.client._get_keystone_session')
    def test_get_endpoint(self, session):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        client = self.create_client(env)
        client.auth_plugin.opts.pop('endpoint')
        client.auth_plugin.opts.pop('token', None)
        alarm_auth_plugin = client.alarm_client.http_client.auth_plugin
        alarm_auth_plugin.opts.pop('endpoint')
        alarm_auth_plugin.opts.pop('token', None)

        self.assertNotEqual(client.auth_plugin, alarm_auth_plugin)

        client.auth_plugin._do_authenticate(mock.MagicMock())
        alarm_auth_plugin._do_authenticate(mock.MagicMock())

        self.assertEqual([
            mock.call(interface='publicURL', region_name=None,
                      service_type='metering'),
            mock.call(interface='publicURL', region_name=None,
                      service_type='alarming'),
        ], session_instance_mock.get_endpoint.mock_calls)

    def test_http_client_with_session(self):
        session = mock.Mock()
        session.request.return_value = mock.Mock(status_code=404,
                                                 text=b'')
        env = {"session": session,
               "service_type": "metering",
               "user_agent": "python-ceilometerclient"}
        c = client.SessionClient(**env)
        self.assertRaises(exc.HTTPException, c.get, "/")

    def test_get_aodh_endpoint_without_auth_url(self):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)
        env.pop('auth_url', None)
        client = self.create_client(env, endpoint='fake_endpoint')
        self.assertEqual(client.alarm_client.http_client.auth_plugin.opts,
                         client.auth_plugin.opts)

    @mock.patch('ceilometerclient.client._get_keystone_session')
    def test_get_different_endpoint_type(self, session):
        env = FAKE_ENV.copy()
        env.pop('auth_plugin', None)
        env.pop('endpoint', None)
        env['endpoint_type'] = 'internal'

        session_instance_mock = mock.MagicMock()
        session.return_value = session_instance_mock

        client = self.create_client(env)
        client.auth_plugin.opts.pop('endpoint')
        client.auth_plugin.opts.pop('token', None)
        alarm_auth_plugin = client.alarm_client.http_client.auth_plugin
        alarm_auth_plugin.opts.pop('endpoint')
        alarm_auth_plugin.opts.pop('token', None)

        self.assertNotEqual(client.auth_plugin, alarm_auth_plugin)

        client.auth_plugin._do_authenticate(mock.MagicMock())
        alarm_auth_plugin._do_authenticate(mock.MagicMock())

        self.assertEqual([
            mock.call(interface='internal', region_name=None,
                      service_type='metering'),
            mock.call(interface='internal', region_name=None,
                      service_type='alarming'),
        ], session_instance_mock.get_endpoint.mock_calls)

    @mock.patch('ceilometerclient.client._get_keystone_session')
    def test_get_sufficient_options_missing(self, session):
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
        client.auth_plugin.opts.pop('token', None)
        self.assertRaises(exceptions.AuthPluginOptionsMissing,
                          client.auth_plugin.sufficient_options)
