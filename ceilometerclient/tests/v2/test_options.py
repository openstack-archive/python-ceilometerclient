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

from ceilometerclient.tests import utils
from ceilometerclient.v2 import options


class BuildUrlTest(utils.BaseTestCase):

    def test_one(self):
        url = options.build_url('/', [{'field': 'this',
                                       'op': 'gt',
                                       'value': 43}])
        self.assertEqual(url, '/?q.field=this&q.op=gt&q.value=43')

    def test_two(self):
        url = options.build_url('/', [{'field': 'this',
                                       'op': 'gt',
                                       'value': 43},
                                      {'field': 'that',
                                       'op': 'lt',
                                       'value': 88}])
        ops = 'q.op=gt&q.op=lt'
        vals = 'q.value=43&q.value=88'
        fields = 'q.field=this&q.field=that'
        self.assertEqual(url, '/?%s&%s&%s' % (fields, ops, vals))

    def test_default_op(self):
        url = options.build_url('/', [{'field': 'this',
                                       'value': 43}])
        self.assertEqual(url, '/?q.field=this&q.op=&q.value=43')

    def test_one_param(self):
        url = options.build_url('/', None, ['period=60'])
        self.assertEqual(url, '/?period=60')

    def test_two_params(self):
        url = options.build_url('/', None, ['period=60',
                                            'others=value'])
        self.assertEqual(url, '/?period=60&others=value')

    def test_with_data_type(self):
        url = options.build_url('/', [{'field': 'f1',
                                       'value': '10',
                                       'type': 'int'}],
                                with_data_type=True)

        self.assertEqual('/?q.field=f1&q.op=&q.type=int&q.value=10', url)


class CliTest(utils.BaseTestCase):

    def test_one(self):
        ar = options.cli_to_array('this<=34')
        self.assertEqual(ar, [{'field': 'this', 'op': 'le', 'value': '34'}])

    def test_two(self):
        ar = options.cli_to_array('this<=34;that!=foo')
        self.assertEqual(ar, [{'field': 'this', 'op': 'le', 'value': '34'},
                              {'field': 'that', 'op': 'ne', 'value': 'foo'}])

    def test_negative(self):
        ar = options.cli_to_array('this>=-783')
        self.assertEqual(ar, [{'field': 'this', 'op': 'ge', 'value': '-783'}])

    def test_float(self):
        ar = options.cli_to_array('this<=283.347')
        self.assertEqual(ar, [{'field': 'this',
                               'op': 'le', 'value': '283.347'}])

    def test_invalid_seperator(self):
        self.assertRaises(ValueError, options.cli_to_array,
                          'this=2.4,fooo=doof')

    def test_invalid_operator(self):
        self.assertRaises(ValueError, options.cli_to_array,
                          'this=2.4;fooo-doof')

    def test_with_dot(self):
        ar = options.cli_to_array('metadata.this<=34')
        self.assertEqual(ar, [{'field': 'metadata.this',
                               'op': 'le', 'value': '34'}])

    # NOTE(herndon): this tests for backwards compatibility.
    # if with_data_type is not set, then the code should now
    # parse a data type, even though one may be present.
    def test_without_data_type(self):
        ar = options.cli_to_array('hostname=string::localhost')
        self.assertEqual(ar, [{'field': 'hostname',
                               'op': 'eq',
                               'value': 'string::localhost'}])

    def test_with_string_data_type(self):
        ar = options.cli_to_array('hostname=string::localhost',
                                  with_data_type=True)
        self.assertEqual(ar, [{'field': 'hostname',
                               'op': 'eq',
                               'type': 'string',
                               'value': 'localhost'}])

    def test_with_int_data_type(self):
        ar = options.cli_to_array('port=int::1234',
                                  with_data_type=True)
        self.assertEqual(ar, [{'field': 'port',
                               'op': 'eq',
                               'type': 'int',
                               'value': '1234'}])

    def test_with_float_data_type(self):
        ar = options.cli_to_array('average=float::1234.5678',
                                  with_data_type=True)
        self.assertEqual(ar, [{'field': 'average',
                               'op': 'eq',
                               'type': 'float',
                               'value': '1234.5678'}])

    def test_with_datetime_data_type(self):
        ar = options.cli_to_array('timestamp=datetime::sometimestamp',
                                  with_data_type=True)
        self.assertEqual(ar, [{'field': 'timestamp',
                               'op': 'eq',
                               'type': 'datetime',
                               'value': 'sometimestamp'}])

    def test_with_incorrect_type(self):
        ar = options.cli_to_array('timestamp=invalid::sometimestamp',
                                  with_data_type=True)
        self.assertEqual(ar, [{'field': 'timestamp',
                               'op': 'eq',
                               'type': 'string',
                               'value': 'invalid::sometimestamp'}])

    def test_with_single_colon(self):
        ar = options.cli_to_array('timestamp=datetime:sometimestamp',
                                  with_data_type=True)
        self.assertEqual(ar, [{'field': 'timestamp',
                               'op': 'eq',
                               'type': 'string',
                               'value': 'datetime:sometimestamp'}])
