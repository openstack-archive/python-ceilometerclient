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
import re
import six
import sys

from testtools import matchers

from ceilometerclient import shell as base_shell
from ceilometerclient.tests import utils
from ceilometerclient.v2 import alarms
from ceilometerclient.v2 import samples
from ceilometerclient.v2 import shell as ceilometer_shell


class ShellAlarmStateCommandsTest(utils.BaseTestCase):

    ALARM_ID = 'foobar'

    def setUp(self):
        super(ShellAlarmStateCommandsTest, self).setUp()
        self.cc = mock.Mock()
        self.cc.alarms = mock.Mock()
        self.args = mock.Mock()
        self.args.alarm_id = self.ALARM_ID

    def test_alarm_state_get(self):
        ceilometer_shell.do_alarm_state_get(self.cc, self.args)
        self.cc.alarms.get_state.assert_called_once_with(self.ALARM_ID)
        self.assertFalse(self.cc.alarms.set_state.called)

    def test_alarm_state_set(self):
        self.args.state = 'ok'
        ceilometer_shell.do_alarm_state_set(self.cc, self.args)
        self.cc.alarms.set_state.assert_called_once_with(self.ALARM_ID, 'ok')
        self.assertFalse(self.cc.alarms.get_state.called)


class ShellAlarmHistoryCommandTest(utils.BaseTestCase):

    ALARM_ID = '768ff714-8cfb-4db9-9753-d484cb33a1cc'
    FULL_DETAIL = ('{"alarm_actions": [], '
                   '"user_id": "8185aa72421a4fd396d4122cba50e1b5", '
                   '"name": "scombo", '
                   '"timestamp": "2013-10-03T08:58:33.647912", '
                   '"enabled": true, '
                   '"state_timestamp": "2013-10-03T08:58:33.647912", '
                   '"rule": {"operator": "or", "alarm_ids": '
                   '["062cc907-3a9f-4867-ab3b-fa83212b39f7"]}, '
                   '"alarm_id": "768ff714-8cfb-4db9-9753-d484cb33a1cc", '
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
                      'alarm_id': '768ff714-8cfb-4db9-9753-d484cb33a1cc',
                      'project_id': '57d04f24d0824b78b1ea9bcecedbda8f',
                      'type': 'state transition'},
                     {'on_behalf_of': '57d04f24d0824b78b1ea9bcecedbda8f',
                      'user_id': '8185aa72421a4fd396d4122cba50e1b5',
                      'event_id': 'c74a8611-6553-4764-a860-c15a6aabb5d0',
                      'timestamp': '2013-10-03T08:59:28.326000',
                      'detail': '{"description": "combination of one"}',
                      'alarm_id': '768ff714-8cfb-4db9-9753-d484cb33a1cc',
                      'project_id': '57d04f24d0824b78b1ea9bcecedbda8f',
                      'type': 'rule change'},
                     {'on_behalf_of': '57d04f24d0824b78b1ea9bcecedbda8f',
                      'user_id': '8185aa72421a4fd396d4122cba50e1b5',
                      'event_id': '4fd7df9e-190d-4471-8884-dc5a33d5d4bb',
                      'timestamp': '2013-10-03T08:58:33.647000',
                      'detail': FULL_DETAIL,
                      'alarm_id': '768ff714-8cfb-4db9-9753-d484cb33a1cc',
                      'project_id': '57d04f24d0824b78b1ea9bcecedbda8f',
                      'type': 'creation'}]
    TIMESTAMP_RE = (' +\| (\d{4})-(\d{2})-(\d{2})T'
                    '(\d{2})\:(\d{2})\:(\d{2})\.(\d{6}) \| +')

    def setUp(self):
        super(ShellAlarmHistoryCommandTest, self).setUp()
        self.cc = mock.Mock()
        self.cc.alarms = mock.Mock()
        self.args = mock.Mock()
        self.args.alarm_id = self.ALARM_ID

    def _do_test_alarm_history(self, raw_query=None, parsed_query=None):
        self.args.query = raw_query
        orig = sys.stdout
        sys.stdout = six.StringIO()
        history = [alarms.AlarmChange(mock.Mock(), change)
                   for change in self.ALARM_HISTORY]
        self.cc.alarms.get_history.return_value = history

        try:
            ceilometer_shell.do_alarm_history(self.cc, self.args)
            self.cc.alarms.get_history.assert_called_once_with(
                q=parsed_query,
                alarm_id=self.ALARM_ID
            )
            out = sys.stdout.getvalue()
            required = [
                '.*creation%sname: scombo.*' % self.TIMESTAMP_RE,
                '.*rule change%sdescription: combination of one.*' %
                self.TIMESTAMP_RE,
                '.*state transition%sstate: alarm.*' % self.TIMESTAMP_RE,
            ]
            for r in required:
                self.assertThat(out, matchers.MatchesRegex(r, re.DOTALL))
        finally:
            sys.stdout.close()
            sys.stdout = orig

    def test_alarm_all_history(self):
        self._do_test_alarm_history()

    def test_alarm_constrained_history(self):
        parsed_query = [dict(field='timestamp',
                             value='2013-10-03T08:59:28',
                             op='gt',
                             type='')]
        self._do_test_alarm_history(raw_query='timestamp>2013-10-03T08:59:28',
                                    parsed_query=parsed_query)


class ShellAlarmCommandTest(utils.BaseTestCase):

    ALARM_ID = '768ff714-8cfb-4db9-9753-d484cb33a1cc'
    ALARM = {"alarm_actions": ["log://"],
             "ok_actions": [],
             "description": "instance running hot",
             "timestamp": "2013-11-20T10:38:42.206952",
             "enabled": True,
             "state_timestamp": "2013-11-19T17:20:44",
             "threshold_rule": {"meter_name": "cpu_util",
                                "evaluation_periods": 3,
                                "period": 600,
                                "statistic": "avg",
                                "threshold": 99.0,
                                "query": [{"field": "resource_id",
                                           "value": "INSTANCE_ID",
                                           "op": "eq"}],
                                "comparison_operator": "gt"},
             "alarm_id": ALARM_ID,
             "state": "insufficient data",
             "insufficient_data_actions": [],
             "repeat_actions": True,
             "user_id": "528d9b68fa774689834b5c04b4564f8a",
             "project_id": "ed9d4e2be2a748bc80108053cf4598f5",
             "type": "threshold",
             "name": "cpu_high"}

    def setUp(self):
        super(ShellAlarmCommandTest, self).setUp()
        self.cc = mock.Mock()
        self.cc.alarms = mock.Mock()
        self.args = mock.Mock()
        self.args.alarm_id = self.ALARM_ID

    def _do_test_alarm_update_repeat_actions(self, method, repeat_actions):
        self.args.threshold = 42.0
        if repeat_actions is not None:
            self.args.repeat_actions = repeat_actions
        orig = sys.stdout
        sys.stdout = six.StringIO()
        alarm = [alarms.Alarm(mock.Mock(), self.ALARM)]
        self.cc.alarms.get.return_value = alarm
        self.cc.alarms.update.return_value = alarm[0]

        try:
            method(self.cc, self.args)
            args, kwargs = self.cc.alarms.update.call_args
            self.assertEqual(self.ALARM_ID, args[0])
            self.assertEqual(42.0, kwargs.get('threshold'))
            if repeat_actions is not None:
                self.assertEqual(repeat_actions, kwargs.get('repeat_actions'))
            else:
                self.assertFalse('repeat_actions' in kwargs)
        finally:
            sys.stdout.close()
            sys.stdout = orig

    def test_alarm_update_repeat_actions_untouched(self):
        method = ceilometer_shell.do_alarm_update
        self._do_test_alarm_update_repeat_actions(method, None)

    def test_alarm_update_repeat_actions_set(self):
        method = ceilometer_shell.do_alarm_update
        self._do_test_alarm_update_repeat_actions(method, True)

    def test_alarm_update_repeat_actions_clear(self):
        method = ceilometer_shell.do_alarm_update
        self._do_test_alarm_update_repeat_actions(method, False)

    def test_alarm_combination_update_repeat_actions_untouched(self):
        method = ceilometer_shell.do_alarm_combination_update
        self._do_test_alarm_update_repeat_actions(method, None)

    def test_alarm_combination_update_repeat_actions_set(self):
        method = ceilometer_shell.do_alarm_combination_update
        self._do_test_alarm_update_repeat_actions(method, True)

    def test_alarm_combination_update_repeat_actions_clear(self):
        method = ceilometer_shell.do_alarm_combination_update
        self._do_test_alarm_update_repeat_actions(method, False)

    def test_alarm_threshold_update_repeat_actions_untouched(self):
        method = ceilometer_shell.do_alarm_threshold_update
        self._do_test_alarm_update_repeat_actions(method, None)

    def test_alarm_threshold_update_repeat_actions_set(self):
        method = ceilometer_shell.do_alarm_threshold_update
        self._do_test_alarm_update_repeat_actions(method, True)

    def test_alarm_threshold_update_repeat_actions_clear(self):
        method = ceilometer_shell.do_alarm_threshold_update
        self._do_test_alarm_update_repeat_actions(method, False)

    def test_alarm_threshold_create_args(self):
        shell = base_shell.CeilometerShell()
        argv = ['alarm-threshold-create',
                '--name', 'cpu_high',
                '--description', 'instance running hot',
                '--meter-name', 'cpu_util',
                '--threshold', '70.0',
                '--comparison-operator', 'gt',
                '--statistic', 'avg',
                '--period', '600',
                '--evaluation-periods', '3',
                '--alarm-action', 'log://',
                '--alarm-action', 'http://example.com/alarm/state',
                '--query', 'resource_id=INSTANCE_ID']
        _, args = shell.parse_args(argv)

        orig = sys.stdout
        sys.stdout = six.StringIO()
        alarm = alarms.Alarm(mock.Mock(), self.ALARM)
        self.cc.alarms.create.return_value = alarm

        try:
            ceilometer_shell.do_alarm_threshold_create(self.cc, args)
            _, kwargs = self.cc.alarms.create.call_args
            self.assertEqual('cpu_high', kwargs.get('name'))
            self.assertEqual('instance running hot', kwargs.get('description'))
            actions = ['log://', 'http://example.com/alarm/state']
            self.assertEqual(actions, kwargs.get('alarm_actions'))
            self.assertTrue('threshold_rule' in kwargs)
            rule = kwargs['threshold_rule']
            self.assertEqual('cpu_util', rule.get('meter_name'))
            self.assertEqual(70.0, rule.get('threshold'))
            self.assertEqual('gt', rule.get('comparison_operator'))
            self.assertEqual('avg', rule.get('statistic'))
            self.assertEqual(600, rule.get('period'))
            self.assertEqual(3, rule.get('evaluation_periods'))
            query = dict(field='resource_id', type='',
                         value='INSTANCE_ID', op='eq')
            self.assertEqual([query], rule['query'])
        finally:
            sys.stdout.close()
            sys.stdout = orig


class ShellSampleListCommandTest(utils.BaseTestCase):

    METER = 'cpu_util'
    SAMPLES = [{"counter_name": "cpu_util",
                "resource_id": "5dcf5537-3161-4e25-9235-407e1385bd35",
                "timestamp": "2013-10-15T05:50:30",
                "counter_unit": "%",
                "counter_volume": 0.261666666667,
                "counter_type": "gauge"},
               {"counter_name": "cpu_util",
                "resource_id": "87d197e9-9cf6-4c25-bc66-1b1f4cedb52f",
                "timestamp": "2013-10-15T05:50:29",
                "counter_unit": "%",
                "counter_volume": 0.261666666667,
                "counter_type": "gauge"},
               {"counter_name": "cpu_util",
                "resource_id": "5dcf5537-3161-4e25-9235-407e1385bd35",
                "timestamp": "2013-10-15T05:40:30",
                "counter_unit": "%",
                "counter_volume": 0.251247920133,
                "counter_type": "gauge"},
               {"counter_name": "cpu_util",
                "resource_id": "87d197e9-9cf6-4c25-bc66-1b1f4cedb52f",
                "timestamp": "2013-10-15T05:40:29",
                "counter_unit": "%",
                "counter_volume": 0.26,
                "counter_type": "gauge"}]

    def setUp(self):
        super(ShellSampleListCommandTest, self).setUp()
        self.cc = mock.Mock()
        self.cc.alarms = mock.Mock()
        self.args = mock.Mock()
        self.args.meter = self.METER
        self.args.query = None
        self.args.limit = None

    def test_sample_list(self):

        sample_list = [samples.Sample(mock.Mock(), sample)
                       for sample in self.SAMPLES]
        self.cc.samples.list.return_value = sample_list

        org_stdout = sys.stdout
        try:
            sys.stdout = output = six.StringIO()
            ceilometer_shell.do_sample_list(self.cc, self.args)
            self.cc.samples.list.assert_called_once_with(
                meter_name=self.METER,
                q=None,
                limit=None)
        finally:
            sys.stdout = org_stdout

        self.assertEqual(output.getvalue(), '''\
+--------------------------------------+----------+-------+----------------\
+------+---------------------+
| Resource ID                          | Name     | Type  | Volume         \
| Unit | Timestamp           |
+--------------------------------------+----------+-------+----------------\
+------+---------------------+
| 5dcf5537-3161-4e25-9235-407e1385bd35 | cpu_util | gauge | 0.261666666667 \
| %    | 2013-10-15T05:50:30 |
| 87d197e9-9cf6-4c25-bc66-1b1f4cedb52f | cpu_util | gauge | 0.261666666667 \
| %    | 2013-10-15T05:50:29 |
| 5dcf5537-3161-4e25-9235-407e1385bd35 | cpu_util | gauge | 0.251247920133 \
| %    | 2013-10-15T05:40:30 |
| 87d197e9-9cf6-4c25-bc66-1b1f4cedb52f | cpu_util | gauge | 0.26           \
| %    | 2013-10-15T05:40:29 |
+--------------------------------------+----------+-------+----------------\
+------+---------------------+
''')


class ShellSampleCreateCommandTest(utils.BaseTestCase):

    METER = 'instance'
    METER_TYPE = 'gauge'
    RESOURCE_ID = '0564c64c-3545-4e34-abfb-9d18e5f2f2f9'
    SAMPLE_VOLUME = '1'
    METER_UNIT = 'instance'
    SAMPLE = [{
        u'counter_name': u'instance',
        u'user_id': u'21b442b8101d407d8242b6610e0ed0eb',
        u'resource_id': u'0564c64c-3545-4e34-abfb-9d18e5f2f2f9',
        u'timestamp': u'2014-01-10T03: 05: 33.951170',
        u'message_id': u'1247cbe6-79a4-11e3-a296-000c294c58e2',
        u'source': u'384260c6987b451d8290e66e1f108082: openstack',
        u'counter_unit': u'instance',
        u'counter_volume': 1.0,
        u'project_id': u'384260c6987b451d8290e66e1f108082',
        u'resource_metadata': {},
        u'counter_type': u'gauge'
    }]

    def setUp(self):
        super(ShellSampleCreateCommandTest, self).setUp()
        self.cc = mock.Mock()
        self.args = mock.Mock()
        self.args.meter_name = self.METER
        self.args.meter_type = self.METER_TYPE
        self.args.meter_unit = self.METER_UNIT
        self.args.resource_id = self.RESOURCE_ID
        self.args.sample_volume = self.SAMPLE_VOLUME

    def test_sample_create(self):

        ret_sample = [samples.Sample(mock.Mock(), sample)
                      for sample in self.SAMPLE]
        self.cc.samples.create.return_value = ret_sample
        org_stdout = sys.stdout
        try:
            sys.stdout = output = six.StringIO()
            ceilometer_shell.do_sample_create(self.cc, self.args)
        finally:
            sys.stdout = org_stdout

        self.assertEqual(output.getvalue(), '''\
+-------------------+---------------------------------------------+
| Property          | Value                                       |
+-------------------+---------------------------------------------+
| message_id        | 1247cbe6-79a4-11e3-a296-000c294c58e2        |
| name              | instance                                    |
| project_id        | 384260c6987b451d8290e66e1f108082            |
| resource_id       | 0564c64c-3545-4e34-abfb-9d18e5f2f2f9        |
| resource_metadata | {}                                          |
| source            | 384260c6987b451d8290e66e1f108082: openstack |
| timestamp         | 2014-01-10T03: 05: 33.951170                |
| type              | gauge                                       |
| unit              | instance                                    |
| user_id           | 21b442b8101d407d8242b6610e0ed0eb            |
| volume            | 1.0                                         |
+-------------------+---------------------------------------------+
''')
