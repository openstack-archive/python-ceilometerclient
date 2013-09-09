#  Copyright 2013 NEC Corporation.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from ceilometerclient.tests import fakes
from ceilometerclient.v2 import client as v2client
import json


class FakeClient(v2client.Client):

    AN_ALARM = {u'alarm_actions': [u'http://site:8000/alarm'],
                u'ok_actions': [u'http://site:8000/ok'],
                u'description': u'An alarm',
                u'matching_metadata': {u'key_name': u'key_value'},
                u'evaluation_periods': 2,
                u'timestamp': u'2013-05-09T13:41:23.085000',
                u'enabled': True,
                u'counter_name': 'storage.objects',
                u'period': 240.0,
                u'alarm_id': u'alarm-id',
                u'state': u'ok',
                u'insufficient_data_actions': [u'http://site:8000/nodata'],
                u'statistic': u'avg',
                u'threshold': 200.0,
                u'user_id': u'user-id',
                u'project_id': u'project-id',
                u'state_timestamp': u'2013-05-09T13:41:23.085000',
                u'comparison_operator': 'gt',
                u'repeat_actions': False,
                u'name': 'SwiftObjectAlarm'}
    call_stack = []

    def __init__(self, *args, **kwargs):
        super(FakeClient, self).__init__(*args, **kwargs)

    def assert_called(self, method, url, pos=-1):
        called = self.call_stack[pos]
        expected = (method, url)
        assert expected == called, \
            'Expected %s %s but not call were made.' % expected

    def _http_request(self, url, method, **kwargs):

        self.call_stack.append((method, url))

        act_method = method.lower() + url.replace('/', '_')
        status, reason, header, body = getattr(self, act_method)(**kwargs)
        resp = fakes.FakeHTTPResponse(status, '', header, body)
        return resp, body

    def post_v2_alarms(self, **kwargs):
        return (200,
                'OK',
                {'content-type': 'application/json'},
                json.dumps(self.AN_ALARM))

    def put_v2_alarms_foo(self, **kwargs):
        return (200,
                'OK',
                {'content-type': 'application/json'},
                json.dumps(self.AN_ALARM))
