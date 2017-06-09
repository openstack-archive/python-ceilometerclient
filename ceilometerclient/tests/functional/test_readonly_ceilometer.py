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

from ceilometerclient.tests.functional import base
import re


class SimpleReadOnlyCeilometerClientTest(base.ClientTestBase):
    """Basic, read-only tests for Ceilometer CLI client.

    Checks return values and output of read-only commands.
    These tests do not presume any content, nor do they create
    their own. They only verify the structure of output if present.
    """

    def test_ceilometer_meter_list(self):
        result = self.ceilometer('meter-list')
        meters = self.parser.listing(result)
        self.assertTableStruct(meters, ['Name', 'Type', 'Unit',
                                        'Resource ID', 'Project ID'])

    def test_ceilometer_resource_list(self):
        result = self.ceilometer('resource-list')
        resources = self.parser.listing(result)
        self.assertTableStruct(resources, ['Resource ID', 'Source',
                                           'User ID', 'Project ID'])

    def test_ceilometer_alarm_list(self):
        result = self.ceilometer('alarm-list')
        alarm = self.parser.listing(result)
        self.assertTableStruct(alarm, ['Alarm ID', 'Name', 'State',
                                       'Enabled', 'Continuous'])

    def test_admin_help(self):
        help_text = self.ceilometer('help')
        lines = help_text.split('\n')
        self.assertFirstLineStartsWith(lines, 'usage: ceilometer')

        commands = []
        cmds_start = lines.index('Positional arguments:')
        cmds_end = lines.index('Optional arguments:')
        command_pattern = re.compile('^ {4}([a-z0-9\-\_]+)')
        for line in lines[cmds_start:cmds_end]:
            match = command_pattern.match(line)
            if match:
                commands.append(match.group(1))
        commands = set(commands)
        wanted_commands = set(('alarm-combination-create', 'alarm-create',
                               'help', 'alarm-delete', 'event-list'))
        self.assertFalse(wanted_commands - commands)

    def test_ceilometer_bash_completion(self):
        self.ceilometer('bash-completion')

    # Optional arguments

    def test_ceilometer_debug_list(self):
        self.ceilometer('meter-list', flags='--debug')
