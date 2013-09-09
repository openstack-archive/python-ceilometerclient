#  Copyright 2013 NEC Corporation.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ceilometerclient import exc
from ceilometerclient import shell as ceilometer_shell
from ceilometerclient.tests import utils
from ceilometerclient.tests.v2 import fakes
import cStringIO
import fixtures
import sys

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where',
            'CEILOMETER_API_VERSION': '2'}


class ShellTest(utils.BaseTestCase):

    def setUp(self):
        super(ShellTest, self).setUp()
        self.useFixture(fixtures.MonkeyPatch('os.environ', FAKE_ENV))
        self.fc = fakes.FakeClient(endpoint='http://foo.bar')
        self.useFixture(fixtures.MonkeyPatch(
            'ceilometerclient.client.get_client',
            lambda *_, **__: self.fc))
        self.useFixture(fixtures.MonkeyPatch('sys.stdout',
            cStringIO.StringIO()))

    def shell(self, args):
        shell = ceilometer_shell.CeilometerShell()
        shell.main(args)
        return sys.stdout.getvalue()

    def test_do_alarm_create(self):
        args = ['alarm-create']
        self.assertRaises(exc.CommandError, self.shell, args)
        args.extend(['--name', 'foo'])
        self.assertRaises(exc.CommandError, self.shell, args)
        args.extend(['--threshold', '2'])
        self.assertRaises(exc.CommandError, self.shell, args)
        args.extend(['--comparison-operator', 'gt'])
        self.assertRaises(exc.CommandError, self.shell, args)
        args.extend(['--counter-name', 'vcpu'])
        self.assertRaises(exc.CommandError, self.shell, args)
        args.extend(['--statistic', 'count'])
        self.shell(args)
        self.fc.assert_called('POST', '/v2/alarms')

    def test_do_alarm_update(self):
        args = ['alarm-update']
        self.assertRaises(exc.CommandError, self.shell, args)
        args.extend(['-a', 'foo'])
        self.shell(args)
        self.fc.assert_called('PUT', '/v2/alarms/foo')
