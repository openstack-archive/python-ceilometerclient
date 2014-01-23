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

import mock
import types

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
            'auth_plugin': 'fake_auth'}

FAKE_ENV_NO_AUTH_PLUGIN = \
    {'username': 'username',
     'password': 'password',
     'tenant_name': 'tenant_name',
     'auth_url': 'http://no.where',
     'auth_token': '1234',
     }


class ClientTest(utils.BaseTestCase):

    def create_client(self, api_version=2, endpoint=None, exclude=[]):
        env = dict((k, v) for k, v in FAKE_ENV.items()
                   if k not in exclude) if not endpoint else \
            dict((k, v) for k, v in FAKE_ENV_NO_AUTH_PLUGIN.items()
                 if k not in exclude)

        return client.Client(api_version, endpoint, **env)

    def setUp(self):
        super(ClientTest, self).setUp()

    def test_client_version(self):
        c1 = self.create_client(api_version=1)
        self.assertIsInstance(c1, v1client.Client)

        c2 = self.create_client(api_version=2)
        self.assertIsInstance(c2, v2client.Client)

    def test_client_auth_lambda(self):
        FAKE_ENV['auth_token'] = lambda: FAKE_ENV['auth_token']
        self.assertIsInstance(FAKE_ENV['auth_token'],
                              types.FunctionType)
        c2 = self.create_client()
        self.assertIsInstance(c2, v2client.Client)

    def test_client_auth_non_lambda(self):
        FAKE_ENV['auth_token'] = "1234"
        self.assertIsInstance(FAKE_ENV['auth_token'], str)
        c2 = self.create_client()
        self.assertIsInstance(c2, v2client.Client)

    @mock.patch('keystoneclient.v2_0.client', fakes.FakeKeystone)
    def test_client_without_auth_plugin(self):
        c = self.create_client(api_version=2, endpoint='fake_endpoint')
        self.assertIsInstance(c.auth_plugin, client.AuthPlugin)

    def test_client_with_auth_plugin(self):
        c = self.create_client(api_version=2)
        self.assertIsInstance(c.auth_plugin, str)
