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

from ceilometerclient.tests import utils
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
        ceilometer_shell.do_alarm_get_state(self.cc, self.args)
        self.cc.alarms.get_state.assert_called_once_with(self.ALARM_ID)
        self.assertFalse(self.cc.alarms.set_state.called)

    def test_alarm_state_set(self):
        self.args.state = 'ok'
        ceilometer_shell.do_alarm_set_state(self.cc, self.args)
        self.cc.alarms.set_state.assert_called_once_with(self.ALARM_ID, 'ok')
        self.assertFalse(self.cc.alarms.get_state.called)
