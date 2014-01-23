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
    '/v1/projects': {
        'GET': (
            {},
            {'projects': [
                'a',
                'b',
            ]},
        ),
    },
    '/v1/sources/source_b/projects': {
        'GET': (
            {},
            {'projects': ['b']},
        ),
    },
}


class ProjectManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(ProjectManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v1.meters.ProjectManager(self.api)

    def test_list_all(self):
        projects = list(self.mgr.list())
        expect = [
            'GET', '/v1/projects'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(projects), 2)
        self.assertEqual(projects[0].project_id, 'a')
        self.assertEqual(projects[1].project_id, 'b')

    def test_list_by_source(self):
        projects = list(self.mgr.list(source='source_b'))
        expect = [
            'GET', '/v1/sources/source_b/projects'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].project_id, 'b')
