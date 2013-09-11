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
import testtools

from ceilometerclient.tests import utils
import ceilometerclient.v2.alarms


AN_ALARM = {u'alarm_actions': [u'http://site:8000/alarm'],
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
CREATE_ALARM = copy.deepcopy(AN_ALARM)
del CREATE_ALARM['timestamp']
del CREATE_ALARM['state_timestamp']
del CREATE_ALARM['alarm_id']
DELTA_ALARM = {u'alarm_actions': ['url1', 'url2'],
               u'comparison_operator': u'lt',
               u'meter_name': u'foobar',
               u'threshold': 42.1}
UPDATED_ALARM = copy.deepcopy(AN_ALARM)
UPDATED_ALARM.update(DELTA_ALARM)

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
    '/v2/alarms?q.op=&q.op=&q.value=project-id&q.value=SwiftObjectAlarm'
    '&q.field=project_id&q.field=name':
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
}


class AlarmManagerTest(testtools.TestCase):

    def setUp(self):
        super(AlarmManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ceilometerclient.v2.alarms.AlarmManager(self.api)

    def test_list_all(self):
        alarms = list(self.mgr.list())
        expect = [
            ('GET', '/v2/alarms', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(alarms), 1)
        self.assertEqual(alarms[0].alarm_id, 'alarm-id')

    def test_list_with_query(self):
        alarms = list(self.mgr.list(q=[
                                      {"field": "project_id",
                                       "value": "project-id"},
                                      {"field": "name",
                                       "value": "SwiftObjectAlarm"},
                                     ]))
        expect = [
            ('GET',
             '/v2/alarms?q.op=&q.op=&q.value=project-id&q.value='
             'SwiftObjectAlarm&q.field=project_id&q.field=name',
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

    def test_create(self):
        alarm = self.mgr.create(**CREATE_ALARM)
        expect = [
            ('POST', '/v2/alarms', {}, CREATE_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)

    def test_create_legacy(self):
        create = {}
        create.update(CREATE_ALARM)
        create['counter_name'] = CREATE_ALARM['meter_name']
        del create['meter_name']
        alarm = self.mgr.create(**create)
        expect = [
            ('POST', '/v2/alarms', {}, CREATE_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)

    def test_update(self):
        alarm = self.mgr.update(alarm_id='alarm-id', **DELTA_ALARM)
        expect = [
            ('PUT', '/v2/alarms/alarm-id', {}, DELTA_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        for (key, value) in DELTA_ALARM.iteritems():
            self.assertEqual(getattr(alarm, key), value)

    def test_update_legacy(self):
        delta = {}
        delta.update(DELTA_ALARM)
        delta['counter_name'] = DELTA_ALARM['meter_name']
        del delta['meter_name']
        alarm = self.mgr.update(alarm_id='alarm-id', **delta)
        expect = [
            ('PUT', '/v2/alarms/alarm-id', {}, DELTA_ALARM),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(alarm)
        self.assertEqual(alarm.alarm_id, 'alarm-id')
        for (key, value) in DELTA_ALARM.iteritems():
            self.assertEqual(getattr(alarm, key), value)

    def test_delete(self):
        deleted = self.mgr.delete(alarm_id='victim-id')
        expect = [
            ('DELETE', '/v2/alarms/victim-id', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(deleted is None)
