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
import ceilometerclient.v2.statistics

base_url = '/v2/meters/instance/statistics'
qry = ('q.field=resource_id&q.field=source&q.op=&q.op='
       '&q.type=&q.type=&q.value=foo&q.value=bar')
period = '&period=60'
groupby = '&groupby=resource_id'
samples = [
    {u'count': 135,
     u'duration_start': u'2013-02-04T10:51:42',
     u'min': 1.0,
     u'max': 1.0,
     u'duration_end':
     u'2013-02-05T15:46:09',
     u'duration': 1734.0,
     u'avg': 1.0,
     u'sum': 135.0},
]
groupby_samples = [
    {u'count': 135,
     u'duration_start': u'2013-02-04T10:51:42',
     u'min': 1.0,
     u'max': 1.0,
     u'duration_end':
     u'2013-02-05T15:46:09',
     u'duration': 1734.0,
     u'avg': 1.0,
     u'sum': 135.0,
     u'groupby': {u'resource_id': u'foo'}
     },
    {u'count': 12,
     u'duration_start': u'2013-02-04T10:51:42',
     u'min': 1.0,
     u'max': 1.0,
     u'duration_end':
     u'2013-02-05T15:46:09',
     u'duration': 1734.0,
     u'avg': 1.0,
     u'sum': 12.0,
     u'groupby': {u'resource_id': u'bar'}
     },
]
fixtures = {
    base_url:
    {
        'GET': (
            {},
            samples
        ),
    },
    '%s?%s' % (base_url, qry):
    {
        'GET': (
            {},
            samples
        ),
    },
    '%s?%s%s' % (base_url, qry, period):
    {
        'GET': (
            {},
            samples
        ),
    },
    '%s?%s%s' % (base_url, qry, groupby):
    {
        'GET': (
            {},
            groupby_samples
        ),
    },
}


class StatisticsManagerTest(utils.BaseTestCase):

    def setUp(self):
        super(StatisticsManagerTest, self).setUp()
        self.http_client = fake_client.FakeHTTPClient(fixtures=fixtures)
        self.api = client.BaseClient(self.http_client)
        self.mgr = ceilometerclient.v2.statistics.StatisticsManager(self.api)

    def test_list_by_meter_name(self):
        stats = list(self.mgr.list(meter_name='instance'))
        expect = [
            'GET', '/v2/meters/instance/statistics'
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].count, 135)

    def test_list_by_meter_name_extended(self):
        stats = list(self.mgr.list(meter_name='instance',
                                   q=[
                                       {"field": "resource_id",
                                        "value": "foo"},
                                       {"field": "source",
                                        "value": "bar"},
                                   ]))
        expect = [
            'GET', '%s?%s' % (base_url, qry)
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].count, 135)

    def test_list_by_meter_name_with_period(self):
        stats = list(self.mgr.list(meter_name='instance',
                                   q=[
                                       {"field": "resource_id",
                                        "value": "foo"},
                                       {"field": "source",
                                        "value": "bar"},
                                   ],
                                   period=60))
        expect = [
            'GET', '%s?%s%s' % (base_url, qry, period)
        ]
        self.http_client.assert_called(*expect)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].count, 135)

    def test_list_by_meter_name_with_groupby(self):
        stats = list(self.mgr.list(meter_name='instance',
                                   q=[
                                       {"field": "resource_id",
                                        "value": "foo"},
                                       {"field": "source",
                                        "value": "bar"},
                                   ],
                                   groupby=['resource_id']))
        expect = [
            ('GET',
             '%s?%s%s' % (base_url, qry, groupby), {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0].count, 135)
        self.assertEqual(stats[1].count, 12)
        self.assertEqual(stats[0].groupby.get('resource_id'), 'foo')
        self.assertEqual(stats[1].groupby.get('resource_id'), 'bar')
