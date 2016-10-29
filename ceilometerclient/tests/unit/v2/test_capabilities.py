# Copyright 2014 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import testtools

from ceilometerclient.apiclient import client
from ceilometerclient.apiclient import fake_client
from ceilometerclient.v2 import capabilities


CAPABILITIES = {
    "alarm_storage": {
        "storage:production_ready": True
    },
    "api": {
        "alarms:query:complex": True,
        "alarms:query:simple": True
    },
    "event_storage": {
        "storage:production_ready": True
    },
    "storage": {
        "storage:production_ready": True
    },
}

FIXTURES = {
    '/v2/capabilities': {
        'GET': (
            {},
            CAPABILITIES
        ),
    },
}


class CapabilitiesManagerTest(testtools.TestCase):
    def setUp(self):
        super(CapabilitiesManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=FIXTURES)
        self.api = client.BaseClient(self.http_client)
        self.mgr = capabilities.CapabilitiesManager(self.api)

    def test_capabilities_get(self):
        capabilities = self.mgr.get()
        self.http_client.assert_called('GET', '/v2/capabilities')
        self.assertTrue(capabilities.api['alarms:query:complex'])
