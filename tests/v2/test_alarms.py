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

import unittest

import ceilometerclient.v2.alarms
from tests import utils


AN_ALARM = {u'alarm_actions': [u'http://site:8000/alarm'],
            u'ok_actions': [u'http://site:8000/ok'],
            u'description': u'An alarm',
            u'matching_metadata': {u'key_name': u'key_value'},
            u'evaluation_periods': 2,
            u'timestamp': u'2013-05-09T13:41:23.085000',
            u'enabled': True,
            u'counter_name': u'storage.objects',
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
            u'name': 'SwiftObjectAlarm'}

fixtures = {
    '/v2/alarms':
    {
        'GET': (
            {},
            [AN_ALARM],
        ),
    },
    '/v2/alarms?q.op=&q.op=&q.value=project-id&q.value=SwiftObjectAlarm'
    '&q.field=project_id&q.field=name':
    {
        'GET': (
            {},
            [AN_ALARM],
        ),
    }
}


class AlarmManagerTest(unittest.TestCase):

    def setUp(self):
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
