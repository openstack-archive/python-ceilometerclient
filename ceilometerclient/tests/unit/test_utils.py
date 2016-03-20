# Copyright 2013 OpenStack Foundation
# All Rights Reserved.
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

import itertools

import mock
import six

from ceilometerclient.common import utils
from ceilometerclient.tests.unit import utils as test_utils


class UtilsTest(test_utils.BaseTestCase):

    def test_prettytable(self):
        class Struct(object):
            def __init__(self, **entries):
                self.__dict__.update(entries)

        # test that the prettytable output is wellformatted (left-aligned)
        with mock.patch('sys.stdout', new=six.StringIO()) as stdout:
            utils.print_dict({'K': 'k', 'Key': 'Value'})
            self.assertEqual('''\
+----------+-------+
| Property | Value |
+----------+-------+
| K        | k     |
| Key      | Value |
+----------+-------+
''', stdout.getvalue())

        with mock.patch('sys.stdout', new=six.StringIO()) as stdout:
            utils.print_dict({'alarm_id': '262567fd-d79a-4bbb-a9d0-59d879b6',
                              'name': u'\u6d4b\u8bd5',
                              'description': u'\u6d4b\u8bd5',
                              'state': 'insufficient data',
                              'repeat_actions': 'False',
                              'type': 'threshold',
                              'threshold': '1.0',
                              'statistic': 'avg',
                              'alarm_actions': [u'http://something/alarm1',
                                                u'http://something/alarm2'],
                              'ok_actions': [{"get_attr1":
                                              [u"web_server_scaleup_policy1",
                                               u"alarm_url1"]},
                                             {"get_attr2":
                                              [u"web_server_scaleup_policy2",
                                               u"alarm_url2"]}],
                              'time_constraints': '[{name: c1,'
                                                  '\\n  description: test,'
                                                  '\\n  start: 0 18 * * *,'
                                                  '\\n  duration: 1,'
                                                  '\\n  timezone: US}]'},
                             wrap=72)
            expected = u'''\
+------------------+-------------------------------------------------------\
--------+
| Property         | Value                                                 \
        |
+------------------+-------------------------------------------------------\
--------+
| alarm_actions    | ["http://something/alarm1", "http://something/alarm2"]\
        |
| alarm_id         | 262567fd-d79a-4bbb-a9d0-59d879b6                      \
        |
| description      | \u6d4b\u8bd5                                          \
                |
| name             | \u6d4b\u8bd5                                          \
                |
| ok_actions       | [{"get_attr1": ["web_server_scaleup_policy1", "alarm_u\
rl1"]}, |
|                  | {"get_attr2": ["web_server_scaleup_policy2", "alarm_ur\
l2"]}]  |
| repeat_actions   | False                                                 \
        |
| state            | insufficient data                                     \
        |
| statistic        | avg                                                   \
        |
| threshold        | 1.0                                                   \
        |
| time_constraints | [{name: c1,                                           \
        |
|                  |   description: test,                                  \
        |
|                  |   start: 0 18 * * *,                                  \
        |
|                  |   duration: 1,                                        \
        |
|                  |   timezone: US}]                                      \
        |
| type             | threshold                                             \
        |
+------------------+-------------------------------------------------------\
--------+
'''
            # py2 prints str type, py3 prints unicode type
            if six.PY2:
                expected = expected.encode('utf-8')
            self.assertEqual(expected, stdout.getvalue())

    def test_print_list(self):
        class Foo(object):
            def __init__(self, one, two, three):
                self.one = one
                self.two = two
                self.three = three

        foo_list = [
            Foo(10, 'a', 'B'),
            Foo(8, 'c', 'c'),
            Foo(12, '0', 'Z')]

        def do_print_list(sortby):
            with mock.patch('sys.stdout', new=six.StringIO()) as stdout:
                utils.print_list(foo_list,
                                 ['one', 'two', 'three'],
                                 ['1st', '2nd', '3rd'],
                                 {'one': lambda o: o.one * 10},
                                 sortby)
                return stdout.getvalue()

        printed = do_print_list(None)
        self.assertEqual('''\
+-----+-----+-----+
| 1st | 2nd | 3rd |
+-----+-----+-----+
| 100 | a   | B   |
| 80  | c   | c   |
| 120 | 0   | Z   |
+-----+-----+-----+
''', printed)

        printed = do_print_list(0)
        self.assertEqual('''\
+-----+-----+-----+
| 1st | 2nd | 3rd |
+-----+-----+-----+
| 80  | c   | c   |
| 100 | a   | B   |
| 120 | 0   | Z   |
+-----+-----+-----+
''', printed)

        printed = do_print_list(1)
        self.assertEqual('''\
+-----+-----+-----+
| 1st | 2nd | 3rd |
+-----+-----+-----+
| 120 | 0   | Z   |
| 100 | a   | B   |
| 80  | c   | c   |
+-----+-----+-----+
''', printed)

    def test_args_array_to_dict(self):
        my_args = {
            'matching_metadata': ['metadata.key=metadata_value'],
            'other': 'value'
        }
        cleaned_dict = utils.args_array_to_dict(my_args,
                                                "matching_metadata")
        self.assertEqual({
            'matching_metadata': {'metadata.key': 'metadata_value'},
            'other': 'value'
        }, cleaned_dict)

    def test_args_array_to_list_of_dicts(self):
        starts = ['0 11 * * *', '"0 11 * * *"', '\'0 11 * * *\'']
        timezones = [None, 'US/Eastern', '"US/Eastern"', '\'US/Eastern\'']
        descs = [None, 'de sc', '"de sc"', '\'de sc\'']
        for start, tz, desc in itertools.product(starts, timezones, descs):
            my_args = {
                'time_constraints': ['name=const1;start=%s;duration=1'
                                     % start],
                'other': 'value'
            }
            expected = {
                'time_constraints': [dict(name='const1',
                                          start='0 11 * * *',
                                          duration='1')],
                'other': 'value'
            }
            if tz:
                my_args['time_constraints'][0] += ';timezone=%s' % tz
                expected['time_constraints'][0]['timezone'] = 'US/Eastern'
            if desc:
                my_args['time_constraints'][0] += ';description=%s' % desc
                expected['time_constraints'][0]['description'] = 'de sc'

            cleaned = utils.args_array_to_list_of_dicts(my_args,
                                                        'time_constraints')
            self.assertEqual(expected, cleaned)

    def test_key_with_slash_to_nested_dict(self):
        my_args = {
            'combination_rule/alarm_ids': ['id1', 'id2'],
            'combination_rule/operator': 'and',
            'threshold_rule/threshold': 400,
            'threshold_rule/statictic': 'avg',
            'threshold_rule/comparison_operator': 'or',
        }
        nested_dict = utils.key_with_slash_to_nested_dict(my_args)
        self.assertEqual({
            'combination_rule': {'alarm_ids': ['id1', 'id2'],
                                 'operator': 'and'},
            'threshold_rule': {'threshold': 400,
                               'statictic': 'avg',
                               'comparison_operator': 'or'},
        }, nested_dict)

    def test_arg(self):
        @utils.arg(help="not_required_no_default.")
        def not_required_no_default():
            pass
        _, args = not_required_no_default.__dict__['arguments'][0]
        self.assertEqual("not_required_no_default.", args['help'])

        @utils.arg(required=True, help="required_no_default.")
        def required_no_default():
            pass
        _, args = required_no_default.__dict__['arguments'][0]
        self.assertEqual("required_no_default. Required.", args['help'])

        @utils.arg(default=42, help="not_required_default.")
        def not_required_default():
            pass
        _, args = not_required_default.__dict__['arguments'][0]
        self.assertEqual("not_required_default. Defaults to 42.", args['help'])

    def test_merge_nested_dict(self):
        dest = {'key': 'value',
                'nested': {'key2': 'value2',
                           'key3': 'value3',
                           'nested2': {'key': 'value',
                                       'some': 'thing'}}}
        source = {'key': 'modified',
                  'nested': {'key3': 'modified3',
                             'nested2': {'key5': 'value5'}}}
        utils.merge_nested_dict(dest, source, depth=1)

        self.assertEqual({'key': 'modified',
                          'nested': {'key2': 'value2',
                                     'key3': 'modified3',
                                     'nested2': {'key5': 'value5'}}}, dest)

    def test_merge_nested_dict_no_depth(self):
        dest = {'key': 'value',
                'nested': {'key2': 'value2',
                           'key3': 'value3',
                           'nested2': {'key': 'value',
                                       'some': 'thing'}}}
        source = {'key': 'modified',
                  'nested': {'key3': 'modified3',
                             'nested2': {'key5': 'value5'}}}
        utils.merge_nested_dict(dest, source)

        self.assertEqual({'key': 'modified',
                          'nested': {'key3': 'modified3',
                                     'nested2': {'key5': 'value5'}}}, dest)

    @mock.patch('prettytable.PrettyTable')
    def test_format_nested_list_of_dict(self, pt_mock):
        actual_rows = []

        def mock_add_row(row):
            actual_rows.append(row)

        table = mock.Mock()
        table.add_row = mock_add_row
        table.get_string.return_value = "the table"

        test_data = [
            {'column_1': 'value_c', 'column_2': 'value_23'},
            {'column_1': 'value_b', 'column_2': 'value_22'},
            {'column_1': 'value_a', 'column_2': 'value_21'}
        ]
        columns = ['column_1', 'column_2']
        pt_mock.return_value = table

        rval = utils.format_nested_list_of_dict(test_data, columns)
        self.assertEqual("the table", rval)
        self.assertEqual([['value_a', 'value_21'],
                          ['value_b', 'value_22'],
                          ['value_c', 'value_23']],
                         actual_rows)
