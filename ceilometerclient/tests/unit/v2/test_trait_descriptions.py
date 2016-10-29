# Copyright 2014 Hewlett-Packard Development Company, L.P.
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
from ceilometerclient.apiclient import client
from ceilometerclient.apiclient import fake_client
from ceilometerclient.tests.unit import utils
import ceilometerclient.v2.trait_descriptions


fixtures = {
    '/v2/event_types/Foo/traits': {
        'GET': (
            {},
            [
                {'name': 'trait_1', 'type': 'string'},
                {'name': 'trait_2', 'type': 'integer'},
                {'name': 'trait_3', 'type': 'datetime'}
            ]
        ),
    }
}


class TraitDescriptionManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(TraitDescriptionManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = (ceilometerclient.v2.trait_descriptions.
                    TraitDescriptionManager(self.api))

    def test_list(self):
        trait_descriptions = list(self.mgr.list('Foo'))
        expect = [
            'GET', '/v2/event_types/Foo/traits'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(3, len(trait_descriptions))
        for i, vals in enumerate([('trait_1', 'string'),
                                  ('trait_2', 'integer'),
                                  ('trait_3', 'datetime')]):

            name, type = vals
            self.assertEqual(trait_descriptions[i].name, name)
            self.assertEqual(trait_descriptions[i].type, type)
