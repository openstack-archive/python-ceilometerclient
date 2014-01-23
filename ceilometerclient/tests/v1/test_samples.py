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
from ceilometerclient.openstack.common.apiclient import client
from ceilometerclient.openstack.common.apiclient import fake_client
from ceilometerclient.tests import utils
import ceilometerclient.v1.meters


fixtures = {
    '/v1/users/freddy/meters/balls': {
        'GET': (
            {},
            {'events': [
                {
                    'resource_id': 'inst-0045',
                    'project_id': 'melbourne_open',
                    'user_id': 'freddy',
                    'name': 'tennis',
                    'type': 'counter',
                    'unit': 'balls',
                    'volume': 3,
                    'timestamp': None,
                    'resource_metadata': None,
                },
            ]},
        ),
    },
    '/v1/sources/openstack/meters/this': {
        'GET': (
            {},
            {'events': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                    'unit': 'b',
                    'volume': 45,
                    'timestamp': None,
                    'resource_metadata': None,
                },
            ]},
        ),
    },
    '/v1/projects/dig_the_ditch/meters/meters': {
        'GET': (
            {},
            {'events': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'meters',
                    'type': 'counter',
                    'unit': 'meters',
                    'volume': 345,
                    'timestamp': None,
                    'resource_metadata': None,
                },
            ]},
        ),
    },
    '/v1/meters?metadata.zxc_id=foo': {
        'GET': (
            {},
            {'events': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                    'unit': 'meters',
                    'volume': 98,
                    'timestamp': None,
                    'resource_metadata': {'zxc_id': 'foo'},
                },
            ]},
        ),
    },
    '/v1/users/freddy/meters/balls?start_timestamp=now&end_timestamp=now': {
        'GET': (
            {},
            {'events': [
                {
                    'resource_id': 'inst-0045',
                    'project_id': 'melbourne_open',
                    'user_id': 'freddy',
                    'name': 'tennis',
                    'type': 'counter',
                    'unit': 'balls',
                    'volume': 3,
                    'timestamp': 'now',
                    'resource_metadata': None,
                },

            ]},
        ),
    },
    '/v1/meters': {
        'GET': (
            {},
            {'meters': []},
        ),
    },
}


class SampleManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(SampleManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v1.meters.SampleManager(self.api)

    def test_list_all(self):
        samples = list(self.mgr.list(counter_name=None))
        expect = [
            'GET', '/v1/meters'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(samples), 0)

    def test_list_by_source(self):
        samples = list(self.mgr.list(source='openstack',
                                     counter_name='this'))
        expect = [
            'GET', '/v1/sources/openstack/meters/this'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].resource_id, 'b')

    def test_list_by_user(self):
        samples = list(self.mgr.list(user_id='freddy',
                                     counter_name='balls'))
        expect = [
            'GET', '/v1/users/freddy/meters/balls'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].project_id, 'melbourne_open')
        self.assertEqual(samples[0].user_id, 'freddy')
        self.assertEqual(samples[0].volume, 3)

    def test_list_by_project(self):
        samples = list(self.mgr.list(project_id='dig_the_ditch',
                                     counter_name='meters'))
        expect = [
            'GET', '/v1/projects/dig_the_ditch/meters/meters'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].project_id, 'dig_the_ditch')
        self.assertEqual(samples[0].volume, 345)
        self.assertEqual(samples[0].unit, 'meters')

    def test_list_by_metaquery(self):
        samples = list(self.mgr.list(metaquery='metadata.zxc_id=foo',
                                     counter_name='this'))
        expect = [
            'GET', '/v1/meters?metadata.zxc_id=foo'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].resource_metadata['zxc_id'], 'foo')

    def test_list_by_timestamp(self):
        samples = list(self.mgr.list(user_id='freddy',
                                     counter_name='balls',
                                     start_timestamp='now',
                                     end_timestamp='now'))
        expect = [
            'GET',
            '/v1/users/freddy/meters/balls?' +
            'start_timestamp=now&end_timestamp=now'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].project_id, 'melbourne_open')
        self.assertEqual(samples[0].user_id, 'freddy')
        self.assertEqual(samples[0].volume, 3)
