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


ALARM = {"alarm_actions": ["http://site:8000/alarm"],
         "alarm_id": None,
         "combination_rule": {
             "alarm_ids": [
                 "739e99cb-c2ec-4718-b900-332502355f38",
                 "153462d0-a9b8-4b5b-8175-9e4b05e9b856"],
             "operator": "or"},
         "description": "An alarm",
         "enabled": True,
         "insufficient_data_actions": ["http://site:8000/nodata"],
         "name": "SwiftObjectAlarm",
         "ok_actions": ["http://site:8000/ok"],
         "project_id": "c96c887c216949acbdfbd8b494863567",
         "repeat_actions": False,
         "state": "ok",
         "state_timestamp": "2014-02-20T10:37:15.589860",
         "threshold_rule": None,
         "timestamp": "2014-02-20T10:37:15.589856",
         "type": "combination",
         "user_id": "c96c887c216949acbdfbd8b494863567"}

QUERY = {"filter": {"and": [{"!=": {"state": "ok"}},
                            {"=": {"type": "combination"}}]},
         "orderby": [{"state_timestamp": "desc"}],
         "limit": 10}

base_url = '/v2/query/alarms'
fixtures = {
    base_url:
    {
        'POST': (
            {},
            [ALARM],
        ),
    },
}


class QueryAlarmsManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(QueryAlarmsManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = query.QueryAlarmsManager(self.api)

    def test_query(self):
        alarms = self.mgr.query(**QUERY)
        expect = [
            'POST', '/v2/query/alarms', QUERY,
        ]

        self.http_client.assert_called(*expect)
        self.assertEqual(1, len(alarms))
