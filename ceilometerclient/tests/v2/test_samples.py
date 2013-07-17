# Copyright 2012 OpenStack LLC.
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

import copy

from ceilometerclient.tests import utils
import ceilometerclient.v2.samples

GET_SAMPLE = {u'counter_name': u'instance',
              u'user_id': u'user-id',
              u'resource_id': u'resource-id',
              u'timestamp': u'2012-07-02T10:40:00',
              u'source': u'test_source',
              u'message_id': u'54558a1c-6ef3-11e2-9875-5453ed1bbb5f',
              u'counter_unit': u'',
              u'counter_volume': 1.0,
              u'project_id': u'project1',
              u'resource_metadata': {u'tag': u'self.counter',
                                     u'display_name': u'test-server'},
              u'counter_type': u'cumulative'}
CREATE_SAMPLE = copy.deepcopy(GET_SAMPLE)
del CREATE_SAMPLE['message_id']
del CREATE_SAMPLE['source']

base_url = '/v2/meters/instance'
args = 'q.op=&q.op=&q.value=foo&q.value=bar&q.field=resource_id&q.field=source'
fixtures = {
    base_url:
    {
        'GET': (
            {},
            [GET_SAMPLE]
        ),
        'POST': (
            {},
            [CREATE_SAMPLE],
        ),
    },
    '%s?%s' % (base_url, args):
    {
        'GET': (
            {},
            [],
        ),
    }
}


class SampleManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(SampleManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ceilometerclient.v2.samples.SampleManager(self.api)

    def test_list_by_meter_name(self):
        samples = list(self.mgr.list(meter_name='instance'))
        expect = [
            ('GET', '/v2/meters/instance', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].resource_id, 'resource-id')

    def test_list_by_meter_name_extended(self):
        samples = list(self.mgr.list(meter_name='instance',
                                     q=[
                                         {"field": "resource_id",
                                          "value": "foo"},
                                         {"field": "source",
                                          "value": "bar"},
                                     ]))
        expect = [('GET', '%s?%s' % (base_url, args), {}, None)]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(samples), 0)

    def test_create(self):
        sample = self.mgr.create(**CREATE_SAMPLE)
        expect = [
            ('POST', '/v2/meters/instance', {}, [CREATE_SAMPLE]),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(sample)
