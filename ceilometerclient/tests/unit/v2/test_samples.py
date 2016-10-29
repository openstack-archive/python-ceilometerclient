# Copyright 2012 OpenStack Foundation
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

from ceilometerclient.apiclient import client
from ceilometerclient.apiclient import fake_client
from ceilometerclient.tests.unit import utils
import ceilometerclient.v2.samples

GET_OLD_SAMPLE = {u'counter_name': u'instance',
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
CREATE_SAMPLE = copy.deepcopy(GET_OLD_SAMPLE)
del CREATE_SAMPLE['message_id']
del CREATE_SAMPLE['source']
CREATE_LIST_SAMPLE = copy.deepcopy(CREATE_SAMPLE)
CREATE_LIST_SAMPLE['counter_name'] = 'image'

GET_SAMPLE = {
    "user_id": None,
    "resource_id": "9b651dfd-7d30-402b-972e-212b2c4bfb05",
    "timestamp": "2014-11-03T13:37:46",
    "meter": "image",
    "volume": 1.0,
    "source": "openstack",
    "recorded_at": "2014-11-03T13:37:46.994458",
    "project_id": "2cc3a7bb859b4bacbeab0aa9ca673033",
    "type": "gauge",
    "id": "98b5f258-635e-11e4-8bdd-0025647390c1",
    "unit": "image",
    "resource_metadata": {},
}

METER_URL = '/v2/meters/instance'
METER_URL_DIRECT = '/v2/meters/instance?direct=True'
SECOND_METER_URL = '/v2/meters/image'
SECOND_METER_URL_DIRECT = '/v2/meters/image?direct=True'
SAMPLE_URL = '/v2/samples'
QUERIES = ('q.field=resource_id&q.field=source&q.op=&q.op='
           '&q.type=&q.type=&q.value=foo&q.value=bar')
LIMIT = 'limit=1'

OLD_SAMPLE_FIXTURES = {
    METER_URL: {
        'GET': (
            {},
            [GET_OLD_SAMPLE]
        ),
        'POST': (
            {},
            [CREATE_SAMPLE],
        ),
    },
    METER_URL_DIRECT: {
        'POST': (
            {},
            [CREATE_SAMPLE],
        )
    },
    SECOND_METER_URL: {
        'POST': (
            {},
            [CREATE_LIST_SAMPLE] * 10,
        ),
    },
    SECOND_METER_URL_DIRECT: {
        'POST': (
            {},
            [CREATE_LIST_SAMPLE] * 10,
        )
    },
    '%s?%s' % (METER_URL, QUERIES): {
        'GET': (
            {},
            [],
        ),
    },
    '%s?%s' % (METER_URL, LIMIT): {
        'GET': (
            {},
            [GET_OLD_SAMPLE]
        ),
    }
}
SAMPLE_FIXTURES = {
    SAMPLE_URL: {
        'GET': (
            (),
            [GET_SAMPLE]
        ),
    },
    '%s?%s' % (SAMPLE_URL, QUERIES): {
        'GET': (
            {},
            [],
        ),
    },
    '%s?%s' % (SAMPLE_URL, LIMIT): {
        'GET': (
            {},
            [GET_SAMPLE],
        ),
    },
    '%s/%s' % (SAMPLE_URL, GET_SAMPLE['id']): {
        'GET': (
            {},
            GET_SAMPLE,
        ),
    },
}


class OldSampleManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(OldSampleManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(
            fixtures=OLD_SAMPLE_FIXTURES)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v2.samples.OldSampleManager(self.api)

    def test_list_by_meter_name(self):
        samples = list(self.mgr.list(meter_name='instance'))
        expect = [
            'GET', '/v2/meters/instance'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(samples))
        self.assertEqual('resource-id', samples[0].resource_id)

    def test_list_by_meter_name_extended(self):
        samples = list(self.mgr.list(meter_name='instance',
                                     q=[
                                         {"field": "resource_id",
                                          "value": "foo"},
                                         {"field": "source",
                                          "value": "bar"},
                                     ]))
        expect = ['GET', '%s?%s' % (METER_URL, QUERIES)]
        self.http_client.assert_called(*expect)
        self.assertEqual(0, len(samples))

    def test_create(self):
        sample = self.mgr.create(**CREATE_SAMPLE)
        expect = [
            'POST', '/v2/meters/instance'
        ]
        self.http_client.assert_called(*expect, body=[CREATE_SAMPLE])
        self.assertIsNotNone(sample)

    def test_create_directly(self):
        sample = self.mgr.create(direct=True, **CREATE_SAMPLE)
        expect = [
            'POST', '/v2/meters/instance?direct=True'
        ]
        self.http_client.assert_called(*expect, body=[CREATE_SAMPLE])
        self.assertIsNotNone(sample)

    def test_create_list(self):
        test_samples = [CREATE_LIST_SAMPLE] * 10
        samples = self.mgr.create_list(test_samples)
        expect = [
            'POST', '/v2/meters/image'
        ]
        self.http_client.assert_called(*expect, body=test_samples)
        self.assertEqual(10, len(samples))

    def test_create_list_directly(self):
        test_samples = [CREATE_LIST_SAMPLE] * 10
        samples = self.mgr.create_list(test_samples, direct=True)
        expect = [
            'POST', '/v2/meters/image?direct=True'
        ]
        self.http_client.assert_called(*expect, body=test_samples)
        self.assertEqual(10, len(samples))

    def test_limit(self):
        samples = list(self.mgr.list(meter_name='instance', limit=1))
        expect = ['GET', '/v2/meters/instance?limit=1']
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(samples))


class SampleManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(SampleManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(
            fixtures=SAMPLE_FIXTURES)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v2.samples.SampleManager(self.api)

    def test_sample_list(self):
        samples = list(self.mgr.list())
        expect = [
            'GET', '/v2/samples'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(samples))
        self.assertEqual('9b651dfd-7d30-402b-972e-212b2c4bfb05',
                         samples[0].resource_id)

    def test_sample_list_with_queries(self):
        queries = [
            {"field": "resource_id",
             "value": "foo"},
            {"field": "source",
             "value": "bar"},
        ]
        samples = list(self.mgr.list(q=queries))
        expect = ['GET', '%s?%s' % (SAMPLE_URL, QUERIES)]
        self.http_client.assert_called(*expect)
        self.assertEqual(0, len(samples))

    def test_sample_list_with_limit(self):
        samples = list(self.mgr.list(limit=1))
        expect = ['GET', '/v2/samples?limit=1']
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(samples))

    def test_sample_get(self):
        sample = self.mgr.get(GET_SAMPLE['id'])
        expect = ['GET', '/v2/samples/' + GET_SAMPLE['id']]
        self.http_client.assert_called(*expect)
        self.assertEqual(GET_SAMPLE, sample.to_dict())
