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
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ceilometerclient.v1.meters.SampleManager(self.api)

    def test_list_all(self):
        samples = list(self.mgr.list(counter_name=None))
        expect = [
            ('GET', '/v1/meters', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(0, len(samples))

    def test_list_by_source(self):
        samples = list(self.mgr.list(source='openstack',
                                     counter_name='this'))
        expect = [
            ('GET', '/v1/sources/openstack/meters/this', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(samples))
        self.assertEqual('b', samples[0].resource_id)

    def test_list_by_user(self):
        samples = list(self.mgr.list(user_id='freddy',
                                     counter_name='balls'))
        expect = [
            ('GET', '/v1/users/freddy/meters/balls', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(samples))
        self.assertEqual('melbourne_open', samples[0].project_id)
        self.assertEqual('freddy', samples[0].user_id)
        self.assertEqual(3, samples[0].volume)

    def test_list_by_project(self):
        samples = list(self.mgr.list(project_id='dig_the_ditch',
                                     counter_name='meters'))
        expect = [
            ('GET', '/v1/projects/dig_the_ditch/meters/meters', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(samples))
        self.assertEqual('dig_the_ditch', samples[0].project_id)
        self.assertEqual(345, samples[0].volume)
        self.assertEqual('meters', samples[0].unit)

    def test_list_by_metaquery(self):
        samples = list(self.mgr.list(metaquery='metadata.zxc_id=foo',
                                     counter_name='this'))
        expect = [
            ('GET', '/v1/meters?metadata.zxc_id=foo', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(samples))
        self.assertEqual('foo', samples[0].resource_metadata['zxc_id'])

    def test_list_by_timestamp(self):
        samples = list(self.mgr.list(user_id='freddy',
                                     counter_name='balls',
                                     start_timestamp='now',
                                     end_timestamp='now'))
        expect = [
            ('GET',
             '/v1/users/freddy/meters/balls?' +
             'start_timestamp=now&end_timestamp=now',
             {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(samples))
        self.assertEqual('melbourne_open', samples[0].project_id)
        self.assertEqual('freddy', samples[0].user_id)
        self.assertEqual(3, samples[0].volume)
