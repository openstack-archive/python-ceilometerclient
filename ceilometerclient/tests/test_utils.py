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


import cStringIO
import sys

from ceilometerclient.common import utils
from ceilometerclient.tests import utils as test_utils


class UtilsTest(test_utils.BaseTestCase):

    def test_prettytable(self):
        class Struct:
            def __init__(self, **entries):
                self.__dict__.update(entries)

        # test that the prettytable output is wellformatted (left-aligned)
        saved_stdout = sys.stdout
        try:
            sys.stdout = output_dict = cStringIO.StringIO()
            utils.print_dict({'K': 'k', 'Key': 'Value'})

        finally:
            sys.stdout = saved_stdout

        self.assertEqual(output_dict.getvalue(), '''\
+----------+-------+
| Property | Value |
+----------+-------+
| K        | k     |
| Key      | Value |
+----------+-------+
''')

    def test_args_array_to_dict(self):
        my_args = {
            'matching_metadata': ['metadata.key=metadata_value'],
            'other': 'value'
        }
        cleaned_dict = utils.args_array_to_dict(my_args,
                                                "matching_metadata")
        self.assertEqual(cleaned_dict, {
            'matching_metadata': {'metadata.key': 'metadata_value'},
            'other': 'value'
        })

    def test_key_with_slash_to_nested_dict(self):
        my_args = {
            'combination_rule/alarm_ids': ['id1', 'id2'],
            'combination_rule/operator': 'and',
            'threshold_rule/threshold': 400,
            'threshold_rule/statictic': 'avg',
            'threshold_rule/comparison_operator': 'or',
        }
        nested_dict = utils.key_with_slash_to_nested_dict(my_args)
        self.assertEqual(nested_dict, {
            'combination_rule': {'alarm_ids': ['id1', 'id2'],
                                 'operator': 'and'},
            'threshold_rule': {'threshold': 400,
                               'statictic': 'avg',
                               'comparison_operator': 'or'},
        })

    def test_arg(self):
        @utils.arg(help="not_required_no_default.")
        def not_required_no_default():
            pass
        _, args = not_required_no_default.__dict__['arguments'][0]
        self.assertEqual(args['help'], "not_required_no_default.")

        @utils.arg(required=True, help="required_no_default.")
        def required_no_default():
            pass
        _, args = required_no_default.__dict__['arguments'][0]
        self.assertEqual(args['help'], "required_no_default. Required.")

        @utils.arg(default=42, help="not_required_default.")
        def not_required_default():
            pass
        _, args = not_required_default.__dict__['arguments'][0]
        self.assertEqual(args['help'], "not_required_default. Defaults to 42.")

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

        self.assertEqual(dest, {'key': 'modified',
                                'nested': {'key2': 'value2',
                                           'key3': 'modified3',
                                           'nested2': {'key5': 'value5'}}})

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

        self.assertEqual(dest, {'key': 'modified',
                                'nested': {'key3': 'modified3',
                                           'nested2': {'key5': 'value5'}}})
