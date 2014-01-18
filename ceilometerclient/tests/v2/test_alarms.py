# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc
#
# Author:  Eoghan Glynn <eglynn@redhat.com>
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

import copy

import six
from six.moves import xrange  # noqa
import testtools

from ceilometerclient.tests import utils
from ceilometerclient.v2 import alarms

AN_ALARM = {u'alarm_actions': [u'http://site:8000/alarm'],
            u'ok_actions': [u'http://site:8000/ok'],
            u'description': u'An alarm',
            u'type': u'threshold',
            u'threshold_rule': {
                u'meter_name': u'storage.objects',
                u'query': [{u'field': u'key_name',
                            u'op': u'eq',
                            u'value': u'key_value'}],
                u'evaluation_periods': 2,
                u'period': 240.0,
                u'statistic': u'avg',
                u'threshold': 200.0,
                u'comparison_operator': 'gt',
            },
            u'timestamp': u'2013-05-09T13:41:23.085000',
            u'enabled': True,
            u'alarm_id': u'alarm-id',
            u'state': u'ok',
            u'insufficient_data_actions': [u'http://site:8000/nodata'],
            u'user_id': u'user-id',
            u'project_id': u'project-id',
            u'state_timestamp': u'2013-05-09T13:41:23.085000',
            u'repeat_actions': False,
            u'name': 'SwiftObjectAlarm'}
CREATE_ALARM = copy.deepcopy(AN_ALARM)
del CREATE_ALARM['timestamp']
del CREATE_ALARM['state_timestamp']
del CREATE_ALARM['alarm_id']
DELTA_ALARM = {u'alarm_actions': ['url1', 'url2']}
DELTA_ALARM_RULE = {u'comparison_operator': u'lt',
                    u'threshold': 42.1,
                    u'meter_name': u'foobar',
                    u'query': [{u'field': u'key_name',
                                u'op': u'eq',
                                u'value': u'key_value'}]}
UPDATED_ALARM = copy.deepcopy(AN_ALARM)
UPDATED_ALARM.update(DELTA_ALARM)
UPDATED_ALARM['threshold_rule'].update(DELTA_ALARM_RULE)
DELTA_ALARM['threshold_rule'] = DELTA_ALARM_RULE
UPDATE_ALARM = copy.deepcopy(UPDATED_ALARM)
del UPDATE_ALARM['user_id']
del UPDATE_ALARM['project_id']
del UPDATE_ALARM['name']
del UPDATE_ALARM['alarm_id']
del UPDATE_ALARM['timestamp']
del UPDATE_ALARM['state_timestamp']

AN_LEGACY_ALARM = {u'alarm_actions': [u'http://site:8000/alarm'],
                   u'ok_actions': [u'http://site:8000/ok'],
                   u'description': u'An alarm',
                   u'matching_metadata': {u'key_name': u'key_value'},
                   u'evaluation_periods': 2,
                   u'timestamp': u'2013-05-09T13:41:23.085000',
                   u'enabled': True,
                   u'meter_name': u'storage.objects',
                   u'period': 240.0,
                   u'alarm_id': u'alarm-id',
                   u'state': u'ok',
                   u'insufficient_data_actions': [u'http://site:8000/nodata'],
                   u'statistic': u'avg',
                   u'threshold': 200.0,
                   u'user_id': u'user-id',
                   u'project_id': u'project-id',
                   u'state_timestamp': u'2013-05-09T13:41:23.085000',
                   u'comparison_operator': 'gt',
                   u'repeat_actions': False,
                   u'name': 'SwiftObjectAlarm'}
CREATE_LEGACY_ALARM = copy.deepcopy(AN_LEGACY_ALARM)
del CREATE_LEGACY_ALARM['timestamp']
del CREATE_LEGACY_ALARM['state_timestamp']
del CREATE_LEGACY_ALARM['alarm_id']
DELTA_LEGACY_ALARM = {u'alarm_actions': ['url1', 'url2'],
                      u'comparison_operator': u'lt',
                      u'meter_name': u'foobar',
                      u'threshold': 42.1}
UPDATED_LEGACY_ALARM = copy.deepcopy(AN_LEGACY_ALARM)
UPDATED_LEGACY_ALARM.update(DELTA_LEGACY_ALARM)
UPDATE_LEGACY_ALARM = copy.deepcopy(UPDATED_LEGACY_ALARM)
del UPDATE_LEGACY_ALARM['user_id']
del UPDATE_LEGACY_ALARM['project_id']
del UPDATE_LEGACY_ALARM['name']
del UPDATE_LEGACY_ALARM['alarm_id']
del UPDATE_LEGACY_ALARM['timestamp']
del UPDATE_LEGACY_ALARM['state_timestamp']

FULL_DETAIL = ('{"alarm_actions": [], '
               '"user_id": "8185aa72421a4fd396d4122cba50e1b5", '
               '"name": "scombo", '
               '"timestamp": "2013-10-03T08:58:33.647912", '
               '"enabled": true, '
               '"state_timestamp": "2013-10-03T08:58:33.647912", '
               '"rule": {"operator": "or", "alarm_ids": '
               '["062cc907-3a9f-4867-ab3b-fa83212b39f7"]}, '
               '"alarm_id": "alarm-id, '
               '"state": "insufficient data", '
               '"insufficient_data_actions": [], '
               '"repeat_actions": false, '
               '"ok_actions": [], '
               '"project_id": "57d04f24d0824b78b1ea9bcecedbda8f", '
               '"type": "combination", '
               '"description": "Combined state of alarms '
               '062cc907-3a9f-4867-ab3b-fa83212b39f7"}')
ALARM_HISTORY = [{'on_behalf_of': '57d04f24d0824b78b1ea9bcecedbda8f',
                  'user_id': '8185aa72421a4fd396d4122cba50e1b5',
                  'event_id': 'c74a8611-6553-4764-a860-c15a6aabb5d0',
                  'timestamp': '2013-10-03T08:59:28.326000',
                  'detail': '{"state": "alarm"}',
                  'alarm_id': 'alarm-id',
                  'project_id': '57d04f24d0824b78b1ea9bcecedbda8f',
                  'type': 'state transition'},
                 {'on_behalf_of': '57d04f24d0824b78b1ea9bcecedbda8f',
                  'user_id': '8185aa72421a4fd396d4122cba50e1b5',
                  'event_id': 'c74a8611-6553-4764-a860-c15a6aabb5d0',
                  'timestamp': '2013-10-03T08:59:28.326000',
                  'detail': '{"description": "combination of one"}',
                  'alarm_id': 'alarm-id',
                  'project_id': '57d04f24d0824b78b1ea9bcecedbda8f',
                  'type': 'rule change'},
                 {'on_behalf_of': '57d04f24d0824b78b1ea9bcecedbda8f',
                  'user_id': '8185aa72421a4fd396d4122cba50e1b5',
                  'event_id': '4fd7df9e-190d-4471-8884-dc5a33d5d4bb',
                  'timestamp': '2013-10-03T08:58:33.647000',
                  'detail': FULL_DETAIL,
                  'alarm_id': 'alarm-id',
                  'project_id': '57d04f24d0824b78b1ea9bcecedbda8f',
                  'type': 'creation'}]

fixtures = {
    '/v2/alarms':
    {
        'GET': (
            {},
            [AN_ALARM],
        ),
        'POST': (
            {},
            CREATE_ALARM,
        ),
    },
    '/v2/alarms/alarm-id':
    {
        'GET': (
            {},
            AN_ALARM,
        ),
        'PUT': (
            {},
            UPDATED_ALARM,
        ),
    },
    '/v2/alarms/alarm-id/state':
    {
        'PUT': (
            {},
            'alarm'
        ),
        'GET': (
            {},
            'alarm'
        ),

    },
    '/v2/alarms?q.field=project_id&q.field=name&q.op=&q.op='
    '&q.type=&q.type=&q.value=project-id&q.value=SwiftObjectAlarm':
    {
        'GET': (
            {},
            [AN_ALARM],
        ),
    },
    '/v2/alarms/victim-id':
    {
        'DELETE': (
            {},
            None,
        ),
    },
    '/v2/alarms/alarm-id/history':
    {
        'GET': (
            {},
            ALARM_HISTORY,
        ),
    },
    '/v2/alarms/alarm-id/history?q.field=timestamp&q.op=&q.type=&q.value=NOW':
    {
        'GET': (
            {},
            ALARM_HISTORY,
        ),
    },
}


class AlarmManagerTest(testtools.TestCase):

    def setUp(self):
        super(AlarmManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = alarms.AlarmManager(self.api)

    def test_list_all(self):
        alarms = list(self.mgr.list())
        expect = [
            ('GET', '/v2/alarms', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(alarms), 1)
        self.assertEqual(alarms[0].alarm_id, 'alarm-id')

    def test_list_with_query(self):
        alarms = list(self.mgr.list(q=[{"field": "project_id",
                                        "value": "project-id"},
                                       {"field": "name",
                                        "value": "SwiftObjectAlarm"}]))
        expect = [
            ('GET',
             '/v2/alarms?q.field=project_id&q.field=name&q.op=&q.op='
             '&q.type=&q.type=&q.value=project-id&q.value=SwiftObjectAlarm',
             {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(alarms), 1)
        self.assertEqual(alarms[0].alarm_id, 'alarm-id')

    def test_get(self):
        alarm = self.mgr.get(alarm_id='alarm-id')
        expect = [
            ('GET', '/v2/alarms/alarm-id', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        self.assertEqual(alarm.rule, alarm.threshold_rule)

    def test_create(self):
        alarm = self.mgr.create(**CREATE_ALARM)
        expect = [
            ('POST', '/v2/alarms', {}, CREATE_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)

    def test_update(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **UPDATE_ALARM)
        expect = [
            ('GET', '/v2/alarms/alarm-id', {}, None),
            ('PUT', '/v2/alarms/alarm-id', {}, UPDATED_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)

    def test_update_delta(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **DELTA_ALARM)
        expect = [
            ('GET', '/v2/alarms/alarm-id', {}, None),
            ('PUT', '/v2/alarms/alarm-id', {}, UPDATED_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)

    def test_set_state(self):
        state = self.mgr.set_state(alarm_id='alarm-id', state='alarm')
        expect = [
            ('PUT', '/v2/alarms/alarm-id/state', {}, 'alarm'),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(state, 'alarm')

    def test_get_state(self):
        state = self.mgr.get_state(alarm_id='alarm-id')
        expect = [
            ('GET', '/v2/alarms/alarm-id/state', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(state, 'alarm')

    def test_delete(self):
        deleted = self.mgr.delete(alarm_id='victim-id')
        expect = [
            ('DELETE', '/v2/alarms/victim-id', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(deleted is None)

    def _do_test_get_history(self, q, url):
        history = self.mgr.get_history(q=q, alarm_id='alarm-id')
        expect = [('GET', url, {}, None)]
        self.assertEqual(self.api.calls, expect)
        for i in xrange(len(history)):
            change = history[i]
            self.assertIsInstance(change, alarms.AlarmChange)
            for k, v in six.iteritems(ALARM_HISTORY[i]):
                self.assertEqual(getattr(change, k), v)

    def test_get_all_history(self):
        url = '/v2/alarms/alarm-id/history'
        self._do_test_get_history(None, url)

    def test_get_constrained_history(self):
        q = [dict(field='timestamp', value='NOW')]
        url = ('/v2/alarms/alarm-id/history?q.field=timestamp'
               '&q.op=&q.type=&q.value=NOW')
        self._do_test_get_history(q, url)


class AlarmLegacyManagerTest(testtools.TestCase):

    def setUp(self):
        super(AlarmLegacyManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = alarms.AlarmManager(self.api)

    def test_create(self):
        alarm = self.mgr.create(**CREATE_LEGACY_ALARM)
        expect = [
            ('POST', '/v2/alarms', {}, CREATE_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)

    def test_create_counter_name(self):
        create = {}
        create.update(CREATE_LEGACY_ALARM)
        create['counter_name'] = CREATE_LEGACY_ALARM['meter_name']
        del create['meter_name']
        alarm = self.mgr.create(**create)
        expect = [
            ('POST', '/v2/alarms', {}, CREATE_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)

    def test_update(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **DELTA_LEGACY_ALARM)
        expect = [
            ('GET', '/v2/alarms/alarm-id', {}, None),
            ('PUT', '/v2/alarms/alarm-id', {}, UPDATED_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)

    def test_update_counter_name(self):
        updated = {}
        updated.update(UPDATE_LEGACY_ALARM)
        updated['counter_name'] = UPDATED_LEGACY_ALARM['meter_name']
        del updated['meter_name']
        alarm = self.mgr.update(alarm_id='alarm-id', **updated)
        expect = [
            ('GET', '/v2/alarms/alarm-id', {}, None),
            ('PUT', '/v2/alarms/alarm-id', {}, UPDATED_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)
