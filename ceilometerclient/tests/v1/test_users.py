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
    '/v1/users': {
        'GET': (
            {},
            {'users': [
                'a',
                'b',
            ]},
        ),
    },
    '/v1/sources/source_b/users': {
        'GET': (
            {},
            {'users': ['b']},
        ),
    },
}


class UserManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(UserManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v1.meters.UserManager(self.api)

    def test_list_all(self):
        users = list(self.mgr.list())
        expect = [
            'GET', '/v1/users'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].user_id, 'a')
        self.assertEqual(users[1].user_id, 'b')

    def test_list_by_source(self):
        users = list(self.mgr.list(source='source_b'))
        expect = [
            'GET', '/v1/sources/source_b/users'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].user_id, 'b')
