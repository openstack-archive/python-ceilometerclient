#
# Copyright 2013 Red Hat, Inc
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

from ceilometerclient.apiclient import client
from ceilometerclient.apiclient import fake_client
from ceilometerclient import exc
from ceilometerclient.v2 import alarms

AN_ALARM = {u'alarm_actions': [u'http://site:8000/alarm'],
            u'ok_actions': [u'http://site:8000/ok'],
            u'description': u'An alarm',
            u'type': u'threshold',
            u'severity': 'low',
            u'threshold_rule': {
                u'meter_name': u'storage.objects',
                u'query': [{u'field': u'key_name',
                            u'op': u'eq',
                            u'value': u'key_value'}],
                u'evaluation_periods': 2,
                u'period': 240.0,
                u'statistic': u'avg',
                u'threshold': 200.0,
                u'comparison_operator': 'gt'},
            u'time_constraints': [
                {
                    u'name': u'cons1',
                    u'description': u'desc1',
                    u'start': u'0 11 * * *',
                    u'duration': 300,
                    u'timezone': u''},
                {
                    u'name': u'cons2',
                    u'description': u'desc2',
                    u'start': u'0 23 * * *',
                    u'duration': 600,
                    u'timezone': ''}],
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
CREATE_ALARM_WITHOUT_TC = copy.deepcopy(CREATE_ALARM)
del CREATE_ALARM_WITHOUT_TC['time_constraints']
DELTA_ALARM = {u'alarm_actions': ['url1', 'url2']}
DELTA_ALARM_RULE = {u'comparison_operator': u'lt',
                    u'threshold': 42.1,
                    u'meter_name': u'foobar',
                    u'query': [{u'field': u'key_name',
                                u'op': u'eq',
                                u'value': u'key_value'}]}
DELTA_ALARM_TC = [{u'name': u'cons1',
                  u'duration': 500}]
DELTA_ALARM['time_constraints'] = DELTA_ALARM_TC
DELTA_ALARM['user_id'] = u'new-user-id'
UPDATED_ALARM = copy.deepcopy(AN_ALARM)
UPDATED_ALARM.update(DELTA_ALARM)
UPDATED_ALARM['threshold_rule'].update(DELTA_ALARM_RULE)
DELTA_ALARM['remove_time_constraints'] = 'cons2'
UPDATED_ALARM['time_constraints'] = [{u'name': u'cons1',
                                      u'description': u'desc1',
                                      u'start': u'0 11 * * *',
                                      u'duration': 500,
                                      u'timezone': u''}]
DELTA_ALARM['threshold_rule'] = DELTA_ALARM_RULE
UPDATE_ALARM = copy.deepcopy(UPDATED_ALARM)
UPDATE_ALARM['remove_time_constraints'] = 'cons2'
UPDATE_ALARM['user_id'] = u'new-user-id'
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
                   u'severity': u'low',
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
DELTA_LEGACY_ALARM['time_constraints'] = [{u'name': u'cons1',
                                           u'duration': 500}]
DELTA_LEGACY_ALARM['user_id'] = u'new-user-id'
DELTA_LEGACY_ALARM['remove_time_constraints'] = 'cons2'
UPDATED_LEGACY_ALARM = copy.deepcopy(AN_LEGACY_ALARM)
UPDATED_LEGACY_ALARM.update(DELTA_LEGACY_ALARM)
UPDATE_LEGACY_ALARM = copy.deepcopy(UPDATED_LEGACY_ALARM)
UPDATE_LEGACY_ALARM['user_id'] = u'new-user-id'
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
        'DELETE': (
            {},
            None,
        ),
    },
    '/v2/alarms/unk-alarm-id':
    {
        'GET': (
            {},
            None,
        ),
        'PUT': (
            {},
            None,
        ),
    },
    '/v2/alarms/alarm-id/state':
    {
        'PUT': (
            {},
            {'alarm': 'alarm'}
        ),
        'GET': (
            {},
            {'alarm': 'alarm'}
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
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = alarms.AlarmManager(self.api)

    def test_list_all(self):
        alarms = list(self.mgr.list())
        expect = [
            'GET', '/v2/alarms'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(alarms))
        self.assertEqual('alarm-id', alarms[0].alarm_id)

    def test_list_with_query(self):
        alarms = list(self.mgr.list(q=[{"field": "project_id",
                                        "value": "project-id"},
                                       {"field": "name",
                                        "value": "SwiftObjectAlarm"}]))
        expect = [
            'GET',
            '/v2/alarms?q.field=project_id&q.field=name&q.op=&q.op='
            '&q.type=&q.type=&q.value=project-id&q.value=SwiftObjectAlarm',
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(alarms))
        self.assertEqual('alarm-id', alarms[0].alarm_id)

    def test_get(self):
        alarm = self.mgr.get(alarm_id='alarm-id')
        expect = [
            'GET', '/v2/alarms/alarm-id'
        ]
        self.http_client.assert_called(*expect)
        self.assertIsNotNone(alarm)
        self.assertEqual('alarm-id', alarm.alarm_id)
        self.assertEqual(alarm.rule, alarm.threshold_rule)

    def test_create(self):
        alarm = self.mgr.create(**CREATE_ALARM)
        expect = [
            'POST', '/v2/alarms'
        ]
        self.http_client.assert_called(*expect, body=CREATE_ALARM)
        self.assertIsNotNone(alarm)

    def test_update(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **UPDATE_ALARM)
        expect_get = [
            'GET', '/v2/alarms/alarm-id'
        ]
        expect_put = [
            'PUT', '/v2/alarms/alarm-id', UPDATED_ALARM
        ]
        self.http_client.assert_called(*expect_get, pos=0)
        self.http_client.assert_called(*expect_put, pos=1)
        self.assertIsNotNone(alarm)
        self.assertEqual('alarm-id', alarm.alarm_id)
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)

    def test_update_delta(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **DELTA_ALARM)
        expect_get = [
            'GET', '/v2/alarms/alarm-id'
        ]
        expect_put = [
            'PUT', '/v2/alarms/alarm-id', UPDATED_ALARM
        ]
        self.http_client.assert_called(*expect_get, pos=0)
        self.http_client.assert_called(*expect_put, pos=1)
        self.assertIsNotNone(alarm)
        self.assertEqual('alarm-id', alarm.alarm_id)
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)

    def test_set_state(self):
        state = self.mgr.set_state(alarm_id='alarm-id', state='alarm')
        expect = [
            'PUT', '/v2/alarms/alarm-id/state'
        ]
        self.http_client.assert_called(*expect, body='alarm')
        self.assertEqual({'alarm': 'alarm'}, state)

    def test_get_state(self):
        state = self.mgr.get_state(alarm_id='alarm-id')
        expect = [
            'GET', '/v2/alarms/alarm-id/state'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual({'alarm': 'alarm'}, state)

    def test_delete(self):
        deleted = self.mgr.delete(alarm_id='victim-id')
        expect = [
            'DELETE', '/v2/alarms/victim-id'
        ]
        self.http_client.assert_called(*expect)
        self.assertIsNone(deleted)

    def test_get_from_alarm_class(self):
        alarm = self.mgr.get(alarm_id='alarm-id')
        self.assertIsNotNone(alarm)
        alarm.get()
        expect = [
            'GET', '/v2/alarms/alarm-id'
        ]
        self.http_client.assert_called(*expect, pos=0)
        self.http_client.assert_called(*expect, pos=1)
        self.assertEqual('alarm-id', alarm.alarm_id)
        self.assertEqual(alarm.threshold_rule, alarm.rule)

    def test_get_state_from_alarm_class(self):
        alarm = self.mgr.get(alarm_id='alarm-id')
        self.assertIsNotNone(alarm)
        state = alarm.get_state()
        expect_get_1 = [
            'GET', '/v2/alarms/alarm-id'
        ]
        expect_get_2 = [
            'GET', '/v2/alarms/alarm-id/state'
        ]
        self.http_client.assert_called(*expect_get_1, pos=0)
        self.http_client.assert_called(*expect_get_2, pos=1)
        self.assertEqual('alarm', state)

    def test_update_missing(self):
        alarm = None
        try:
            alarm = self.mgr.update(alarm_id='unk-alarm-id', **UPDATE_ALARM)
        except exc.CommandError:
            pass
        self.assertIsNone(alarm)

    def test_delete_from_alarm_class(self):
        alarm = self.mgr.get(alarm_id='alarm-id')
        self.assertIsNotNone(alarm)
        deleted = alarm.delete()
        expect_get = [
            'GET', '/v2/alarms/alarm-id'
        ]
        expect_delete = [
            'DELETE', '/v2/alarms/alarm-id'
        ]
        self.http_client.assert_called(*expect_get, pos=0)
        self.http_client.assert_called(*expect_delete, pos=1)
        self.assertIsNone(deleted)

    def _do_test_get_history(self, q, url):
        history = self.mgr.get_history(q=q, alarm_id='alarm-id')
        expect = ['GET', url]
        self.http_client.assert_called(*expect)
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
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = alarms.AlarmManager(self.api)

    def test_create(self):
        alarm = self.mgr.create(**CREATE_LEGACY_ALARM)
        expect = [
            'POST', '/v2/alarms', CREATE_ALARM_WITHOUT_TC,
        ]
        self.http_client.assert_called(*expect)
        self.assertIsNotNone(alarm)

    def test_create_counter_name(self):
        create = {}
        create.update(CREATE_LEGACY_ALARM)
        create['counter_name'] = CREATE_LEGACY_ALARM['meter_name']
        del create['meter_name']
        alarm = self.mgr.create(**create)
        expect = [
            'POST', '/v2/alarms', CREATE_ALARM_WITHOUT_TC,
        ]
        self.http_client.assert_called(*expect)
        self.assertIsNotNone(alarm)

    def test_update(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **DELTA_LEGACY_ALARM)
        expect_put = [
            'PUT', '/v2/alarms/alarm-id', UPDATED_ALARM
        ]
        self.http_client.assert_called(*expect_put)
        self.assertIsNotNone(alarm)
        self.assertEqual('alarm-id', alarm.alarm_id)
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)

    def test_update_counter_name(self):
        updated = {}
        updated.update(UPDATE_LEGACY_ALARM)
        updated['counter_name'] = UPDATED_LEGACY_ALARM['meter_name']
        del updated['meter_name']
        alarm = self.mgr.update(alarm_id='alarm-id', **updated)
        expect_put = [
            'PUT', '/v2/alarms/alarm-id', UPDATED_ALARM
        ]
        self.http_client.assert_called(*expect_put)
        self.assertIsNotNone(alarm)
        self.assertEqual('alarm-id', alarm.alarm_id)
        for (key, value) in six.iteritems(UPDATED_ALARM):
            self.assertEqual(getattr(alarm, key), value)


class AlarmTimeConstraintTest(testtools.TestCase):

    def setUp(self):
        super(AlarmTimeConstraintTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = alarms.AlarmManager(self.api)

    def test_add_new(self):
        new_constraint = dict(name='cons3',
                              start='0 0 * * *',
                              duration=500)
        kwargs = dict(time_constraints=[new_constraint])
        self.mgr.update(alarm_id='alarm-id', **kwargs)
        body = copy.deepcopy(AN_ALARM)
        body[u'time_constraints'] = \
            AN_ALARM[u'time_constraints'] + [new_constraint]
        expect = [
            'PUT', '/v2/alarms/alarm-id', body
        ]
        self.http_client.assert_called(*expect)

    def test_update_existing(self):
        updated_constraint = dict(name='cons2',
                                  duration=500)
        kwargs = dict(time_constraints=[updated_constraint])
        self.mgr.update(alarm_id='alarm-id', **kwargs)
        body = copy.deepcopy(AN_ALARM)
        body[u'time_constraints'][1] = dict(name='cons2',
                                            description='desc2',
                                            start='0 23 * * *',
                                            duration=500,
                                            timezone='')

        expect = [
            'PUT', '/v2/alarms/alarm-id', body
        ]
        self.http_client.assert_called(*expect)

    def test_update_time_constraint_no_name(self):
        updated_constraint = {
            'start': '0 23 * * *',
            'duration': 500
        }
        kwargs = dict(time_constraints=[updated_constraint])
        self.mgr.update(alarm_id='alarm-id', **kwargs)
        body = copy.deepcopy(AN_ALARM)
        body[u'time_constraints'].append({
            'start': '0 23 * * *',
            'duration': 500,
        })
        expect = [
            'PUT', '/v2/alarms/alarm-id', body
        ]
        self.http_client.assert_called(*expect)

    def test_remove(self):
        kwargs = dict(remove_time_constraints=['cons2'])
        self.mgr.update(alarm_id='alarm-id', **kwargs)
        body = copy.deepcopy(AN_ALARM)
        body[u'time_constraints'] = AN_ALARM[u'time_constraints'][:1]
        expect = [
            'PUT', '/v2/alarms/alarm-id', body
        ]
        self.http_client.assert_called(*expect)
