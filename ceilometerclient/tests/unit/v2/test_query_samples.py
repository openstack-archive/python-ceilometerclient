# Copyright Ericsson AB 2014. All rights reserved
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
from ceilometerclient.v2 import query


SAMPLE = {u'id': u'b55d1526-9929-11e3-a3f6-02163e5df1e6',
          u'metadata': {
              u'name1': u'value1',
              u'name2': u'value2'},
          u'meter': 'instance',
          u'project_id': u'35b17138-b364-4e6a-a131-8f3099c5be68',
          u'resource_id': u'bd9431c1-8d69-4ad3-803a-8d4a6b89fd36',
          u'source': u'openstack',
          u'timestamp': u'2014-02-19T05:50:16.673604',
          u'type': u'gauge',
          u'unit': u'instance',
          u'volume': 1,
          u'user_id': 'efd87807-12d2-4b38-9c70-5f5c2ac427ff'}

QUERY = {"filter": {"and": [{"=": {"source": "openstack"}},
                            {">": {"timestamp": "2014-02-19T05:50:16"}}]},
         "orderby": [{"timestamp": "desc"}, {"volume": "asc"}],
         "limit": 10}

base_url = '/v2/query/samples'
fixtures = {
    base_url:
    {
        'POST': (
            {},
            [SAMPLE],
        ),
    },
}


class QuerySamplesManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(QuerySamplesManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = query.QuerySamplesManager(self.api)

    def test_query(self):
        samples = self.mgr.query(**QUERY)
        expect = [

            'POST', '/v2/query/samples', QUERY,
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(samples))
