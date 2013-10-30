# -*- encoding: utf-8 -*-
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

from ceilometerclient.tests import utils
import ceilometerclient.v2.events


fixtures = {
    '/v2/events': {
        'GET': (
            {},
            [
                {
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'message_id': '1'},
                },
                {
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'def',
                               'message_id': '2'},
                },
                {
                    'event_type': 'Bar',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_B': 'bartrait',
                               'message_id': '3'},
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
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'hostname': 'localhost',
                               'message_id': '1'},
                },
                {
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'def',
                               'hostname': 'localhost',
                               'message_id': '2'},
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
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'hostname': 'foreignhost',
                               'message_id': '1'},
                },
                {
                    'event_type': 'Foo',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'def',
                               'hostname': 'foreignhost',
                               'message_id': '2'},
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
                    'event_type': 'Bar',
                    'generated': '1970-01-01T00:00:00',
                    'traits': {'trait_A': 'abc',
                               'hostname': 'localhost',
                               'num_cpus': '5',
                               'message_id': '1'},
                },
            ]
        ),
    },

    '/v2/events/2':
    {
        'GET': (
            {},
            {
                'event_type': 'Foo',
                'generated': '1970-01-01T00:00:00',
                'traits': {'trait_A': 'def',
                           'message_id': '2',
                           'intTrait': '42'},
            }
        ),
    },
}


class EventManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(EventManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ceilometerclient.v2.events.EventManager(self.api)

    def test_list_all(self):
        events = list(self.mgr.list())
        expect = [
            ('GET', '/v2/events', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(events), 3)
        self.assertEqual(events[0].event_type, 'Foo')
        self.assertEqual(events[1].event_type, 'Foo')
        self.assertEqual(events[2].event_type, 'Bar')

    def test_list_one(self):
        event = self.mgr.get(2)
        expect = [
            ('GET', '/v2/events/2', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(event)
        self.assertEqual(event.event_type, 'Foo')

    def test_list_with_query(self):
        events = list(self.mgr.list(q=[{"field": "hostname",
                                        "value": "localhost",
                                        "type": "string"}]))
        expect = [
            ('GET', '/v2/events?q.field=hostname&q.op=&q.type=string'
                    '&q.value=localhost',
             {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, 'Foo')

    def test_list_with_query_no_type(self):
        events = list(self.mgr.list(q=[{"field": "hostname",
                                        "value": "foreignhost"}]))
        expect = [
            ('GET', '/v2/events?q.field=hostname&q.op='
                    '&q.type=&q.value=foreignhost',
             {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].event_type, 'Foo')

    def test_list_with_multiple_filters(self):
        events = list(self.mgr.list(q=[{"field": "hostname",
                                        "value": "localhost"},
                                       {"field": "num_cpus",
                                        "value": "5",
                                        "type": "integer"}]))

        expect = [
            ('GET', '/v2/events?q.field=hostname&q.field=num_cpus&q.op=&q.op='
                    '&q.type=&q.type=integer&q.value=localhost&q.value=5',
             {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(events), 1)
