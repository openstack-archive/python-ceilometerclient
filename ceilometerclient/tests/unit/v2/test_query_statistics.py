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
from ceilometerclient.tests.unit import utils
from ceilometerclient.v2 import query

STATISTIC = {
    u'aggregate': {u'count': 2.0},
    u'count': 2,
    u'duration': 0.442451,
    u'duration_end': u'2015-07-14T12:01:37.728738',
    u'duration_start': u'2015-07-14T12:01:37.673023',
    u'groupby': None,
    u'period': 1,
    u'period_end': u'2015-07-14T12:01:37.673023',
    u'period_start': u'2015-07-14T12:01:38.673023',
    u'unit': u'instance'
}

QUERY = {"filter": {"and": [{"=": {"source": "openstack"}},
                            {">": {
                                "timestamp": "2015-07-14T12:01:37.673022"}}]},
         "period": 1,
         "aggregate": [{"func": "count"}]}

base_url = '/v2/query/statistics'
fixtures = {
    base_url:
    {
        'POST': (
            {},
            [STATISTIC],
        ),
    },
}


class QueryStatisticsManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(QueryStatisticsManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = query.QueryStatisticsManager(self.api)

    def test_query(self):
        statistics = self.mgr.query(**QUERY)
        expect = [
            'POST', '/v2/query/statistics', QUERY,
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(statistics))
