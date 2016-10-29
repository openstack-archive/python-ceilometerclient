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
from ceilometerclient.apiclient import client
from ceilometerclient.apiclient import fake_client
from ceilometerclient.tests.unit import utils
import ceilometerclient.v2.events


fixtures = {
    '/v2/events': {
        'GET': (
            {},
            [
                {
                    'message_id': '1',
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc'},
                },
                {
                    'message_id': '2',
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'def'},
                },
                {
                    'message_id': '3',
                    'event_type': 'Bar',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_B': 'bartrait'},
                },
            ]
        ),
    },
    '/v2/events?q.field=hostname&q.op=&q.type=string&q.value=localhost':
    {
        'GET': (
            {},
            [
                {
                    'message_id': '1',
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'hostname': 'localhost'},
                },
                {
                    'message_id': '2',
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'def',
                               'hostname': 'localhost'},
                }
            ]
        ),
    },
    '/v2/events?q.field=hostname&q.op=&q.type=&q.value=foreignhost':
    {
        'GET': (
            {},
            [
                {
                    'message_id': '1',
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'hostname': 'foreignhost'},
                },
                {
                    'message_id': '2',
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'def',
                               'hostname': 'foreignhost'},
                }
            ]
        ),
    },
    '/v2/events?q.field=hostname&q.field=num_cpus&q.op=&q.op='
    '&q.type=&q.type=integer&q.value=localhost&q.value=5':
    {
        'GET': (
            {},
            [
                {
                    'message_id': '1',
                    'event_type': 'Bar',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'hostname': 'localhost',
                               'num_cpus': '5'},
                },
            ]
        ),
    },

    '/v2/events/2':
    {
        'GET': (
            {},
            {
                'message_id': '2',
                'event_type': 'Foo',
                'generated': '1970-01-01T00:00:00',
                'traits': {'trait_A': 'def',
                           'intTrait': '42'},
            }
        ),
    },
}


class EventManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(EventManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v2.events.EventManager(self.api)

    def test_list_all(self):
        events = list(self.mgr.list())
        expect = [
            'GET', '/v2/events'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(3, len(events))
        self.assertEqual('Foo', events[0].event_type)
        self.assertEqual('Foo', events[1].event_type)
        self.assertEqual('Bar', events[2].event_type)

    def test_list_one(self):
        event = self.mgr.get(2)
        expect = [
            'GET', '/v2/events/2'
        ]
        self.http_client.assert_called(*expect)
        self.assertIsNotNone(event)
        self.assertEqual('Foo', event.event_type)

    def test_list_with_query(self):
        events = list(self.mgr.list(q=[{"field": "hostname",
                                        "value": "localhost",
                                        "type": "string"}]))
        expect = [
            'GET', '/v2/events?q.field=hostname&q.op=&q.type=string'
            '&q.value=localhost'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(2, len(events))
        self.assertEqual('Foo', events[0].event_type)

    def test_list_with_query_no_type(self):
        events = list(self.mgr.list(q=[{"field": "hostname",
                                        "value": "foreignhost"}]))
        expect = [
            'GET', '/v2/events?q.field=hostname&q.op='
            '&q.type=&q.value=foreignhost'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(2, len(events))
        self.assertEqual('Foo', events[0].event_type)

    def test_list_with_multiple_filters(self):
        events = list(self.mgr.list(q=[{"field": "hostname",
                                        "value": "localhost"},
                                       {"field": "num_cpus",
                                        "value": "5",
                                        "type": "integer"}]))

        expect = [
            'GET', '/v2/events?q.field=hostname&q.field=num_cpus&q.op=&q.op='
            '&q.type=&q.type=integer&q.value=localhost&q.value=5'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(events))

    def test_get_from_event_class(self):
        event = self.mgr.get(2)
        self.assertIsNotNone(event)
        event.get()
        expect = [
            'GET', '/v2/events/2'
        ]
        self.http_client.assert_called(*expect, pos=0)
        self.http_client.assert_called(*expect, pos=1)
        self.assertEqual('Foo', event.event_type)
