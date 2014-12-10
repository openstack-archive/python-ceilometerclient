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

from keystoneclient.v2_0 import client as ksclient


def script_keystone_client():
    ksclient.Client(auth_url='http://no.where',
                    insecure=False,
                    password='password',
                    tenant_id='',
                    tenant_name='tenant_name',
                    username='username').AndReturn(FakeKeystone('abcd1234'))


def fake_headers():
    return {'X-Auth-Token': 'abcd1234',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'python-ceilometerclient'}


class FakeServiceCatalog(object):
    @staticmethod
    def url_for(endpoint_type, service_type):
        return 'http://192.168.1.5:8004/v1/f14b41234'


class FakeKeystone(object):
    service_catalog = FakeServiceCatalog()

    def __init__(self, auth_token):
        self.auth_token = auth_token


class FakeHTTPResponse(object):

    version = 1.1

    def __init__(self, status, reason, headers, body):
        self.headers = headers
        self.body = body
        self.status = status
        self.reason = reason

    def getheader(self, name, default=None):
        return self.headers.get(name, default)

    def getheaders(self):
        return self.headers.items()

    def read(self, amt=None):
        b = self.body
        self.body = None
        return b
