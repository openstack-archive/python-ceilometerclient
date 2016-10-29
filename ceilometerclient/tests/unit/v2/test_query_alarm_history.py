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


ALARMCHANGE = {"alarm_id": "e8ff32f772a44a478182c3fe1f7cad6a",
               "event_id": "c74a8611-6553-4764-a860-c15a6aabb5d0",
               "detail": "{\"threshold\": 42.0, \"evaluation_periods\": 4}",
               "on_behalf_of": "92159030020611e3b26dde429e99ee8c",
               "project_id": "b6f16144010811e387e4de429e99ee8c",
               "timestamp": "2014-03-11T16:02:58.376261",
               "type": "rule change",
               "user_id": "3e5d11fda79448ac99ccefb20be187ca"
               }

QUERY = {"filter": {"and": [{">": {"timestamp": "2014-03-11T16:02:58"}},
                            {"=": {"type": "rule change"}}]},
         "orderby": [{"timestamp": "desc"}],
         "limit": 10}

base_url = '/v2/query/alarms/history'
fixtures = {
    base_url:
    {
        'POST': (
            {},
            [ALARMCHANGE],
        ),
    },
}


class QueryAlarmsManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(QueryAlarmsManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = query.QueryAlarmHistoryManager(self.api)

    def test_query(self):
        alarm_history = self.mgr.query(**QUERY)
        expect = [

            'POST', '/v2/query/alarms/history', QUERY,

        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(alarm_history))
