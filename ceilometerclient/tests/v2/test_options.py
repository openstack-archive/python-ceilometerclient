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
        self.assertEqual(url, '/?q.op=gt&q.value=43&q.field=this')

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
        self.assertEqual(url, '/?%s&%s&%s' % (ops, vals, fields))

    def test_default_op(self):
        url = options.build_url('/', [{'field': 'this',
                                       'value': 43}])
        self.assertEqual(url, '/?q.op=&q.value=43&q.field=this')

    def test_one_param(self):
        url = options.build_url('/', None, ['period=60'])
        self.assertEqual(url, '/?period=60')

    def test_two_params(self):
        url = options.build_url('/', None, ['period=60',
                                            'others=value'])
        self.assertEqual(url, '/?period=60&others=value')


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
