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

import cStringIO
import mock
import re
import sys

from testtools import matchers

from ceilometerclient.tests import utils
from ceilometerclient.v2 import alarms
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
        sys.stdout = cStringIO.StringIO()
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
                             op='gt')]
        self._do_test_alarm_history(raw_query='timestamp>2013-10-03T08:59:28',
                                    parsed_query=parsed_query)
