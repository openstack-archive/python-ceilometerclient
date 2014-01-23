# Copyright 2014 Hewlett-Packard Development Company, L.P.
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


from ceilometerclient.openstack.common.apiclient import client
from ceilometerclient.openstack.common.apiclient import fake_client
from ceilometerclient.tests import utils
import ceilometerclient.v2.event_types


fixtures = {
    '/v2/event_types/': {
        'GET': (
            {},
            ['Foo', 'Bar', 'Sna', 'Fu']
        ),
    }
}


class EventTypesManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(EventTypesManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v2.event_types.EventTypeManager(self.api)

    def test_list(self):
        event_types = list(self.mgr.list())
        expect = [
            'GET', '/v2/event_types/'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(event_types), 4)
        self.assertEqual(event_types[0].event_type, "Foo")
        self.assertEqual(event_types[1].event_type, "Bar")
        self.assertEqual(event_types[2].event_type, "Sna")
        self.assertEqual(event_types[3].event_type, "Fu")
