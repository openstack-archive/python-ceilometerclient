# Copyright 2013 OpenStack LLC.
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
