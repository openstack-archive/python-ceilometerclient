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
    '/v1/meters': {
        'GET': (
            {},
            {'meters': [
                {
                    'resource_id': 'a',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'freddy',
                    'name': 'this',
                    'type': 'counter',
                },
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                },
            ]},
        ),
    },
    '/v1/users/joey/meters': {
        'GET': (
            {},
            {'meters': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                },
            ]},
        ),
    },
    '/v1/projects/dig_the_ditch/meters': {
        'GET': (
            {},
            {'meters': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                },
            ]},
        ),
    },
    '/v1/sources/openstack/meters': {
        'GET': (
            {},
            {'meters': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                },
                {
                    'resource_id': 'q',
                    'project_id': 'dig_the_trench',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                },
            ]},
        ),
    },
    '/v1/meters?metadata.zxc_id=foo': {
        'GET': (
            {},
            {'meters': [
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'name': 'this',
                    'type': 'counter',
                },
            ]},
        ),
    },
}


class MeterManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(MeterManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v1.meters.MeterManager(self.api)

    def test_list_all(self):
        resources = list(self.mgr.list())
        expect = [
            'GET', '/v1/meters'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0].resource_id, 'a')
        self.assertEqual(resources[1].resource_id, 'b')

    def test_list_by_source(self):
        resources = list(self.mgr.list(source='openstack'))
        expect = [
            'GET', '/v1/sources/openstack/meters'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0].resource_id, 'b')
        self.assertEqual(resources[1].resource_id, 'q')

    def test_list_by_user(self):
        resources = list(self.mgr.list(user_id='joey'))
        expect = [
            'GET', '/v1/users/joey/meters'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].resource_id, 'b')

    def test_list_by_project(self):
        resources = list(self.mgr.list(project_id='dig_the_ditch'))
        expect = [
            'GET', '/v1/projects/dig_the_ditch/meters'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].resource_id, 'b')

    def test_list_by_metaquery(self):
        resources = list(self.mgr.list(metaquery='metadata.zxc_id=foo'))
        expect = [
            'GET', '/v1/meters?metadata.zxc_id=foo'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].resource_id, 'b')
