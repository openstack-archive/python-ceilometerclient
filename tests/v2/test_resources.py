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

import unittest

import ceilometerclient.v2.resources
from tests import utils


fixtures = {
    '/v2/resources': {
        'GET': (
            {},
            [
                {
                    'resource_id': 'a',
                    'project_id': 'project_bla',
                    'user_id': 'freddy',
                    'metadata': {'zxc_id': 'bla'},
                },
                {
                    'resource_id': 'b',
                    'project_id': 'dig_the_ditch',
                    'user_id': 'joey',
                    'metadata': {'zxc_id': 'foo'},
                },
            ]
        ),
    },
    '/v2/resources?q.op=&q.value=a&q.field=resource_id':
    {
        'GET': (
            {},
            [
                {
                    'resource_id': 'a',
                    'project_id': 'project_bla',
                    'user_id': 'freddy',
                    'metadata': {'zxc_id': 'bla'},
                },
            ]
        ),
    },
    '/v2/resources/a':
    {
        'GET': (
            {},
            {
                'resource_id': 'a',
                'project_id': 'project_bla',
                'user_id': 'freddy',
                'metadata': {'zxc_id': 'bla'},
            },
        ),
    },
}


class ResourceManagerTest(unittest.TestCase):

    def setUp(self):
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ceilometerclient.v2.resources.ResourceManager(self.api)

    def test_list_all(self):
        resources = list(self.mgr.list())
        expect = [
            ('GET', '/v2/resources', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0].resource_id, 'a')
        self.assertEqual(resources[1].resource_id, 'b')

    def test_list_one(self):
        resource = self.mgr.get(resource_id='a')
        expect = [
            ('GET', '/v2/resources/a', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(resource)
        self.assertEqual(resource.resource_id, 'a')

    def test_list_by_query(self):
        resources = list(self.mgr.list(q=[{"field": "resource_id",
                                           "value": "a"},
                                          ]))
        expect = [
            ('GET', '/v2/resources?q.op=&q.value=a&q.field=resource_id',
             {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].resource_id, 'a')
