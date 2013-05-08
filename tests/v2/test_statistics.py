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

import ceilometerclient.v2.statistics
from tests import utils

base_url = '/v2/meters/instance/statistics'
args = 'q.op=&q.op=&q.value=foo&q.value=bar&q.field=resource_id&q.field=source'
fixtures = {
    base_url:
    {
        'GET': (
            {},
            [{
                u'count': 135,
                u'duration_start': u'2013-02-04T10:51:42',
                u'min': 1.0,
                u'max': 1.0,
                u'duration_end':
                u'2013-02-05T15:46:09',
                u'duration': 1734.0,
                u'avg': 1.0,
                u'sum': 135.0,
            }]
        ),
    },
    '%s?%s' % (base_url, args):
    {
        'GET': (
            {},
            [{
                u'count': 135,
                u'duration_start': u'2013-02-04T10:51:42',
                u'min': 1.0,
                u'max': 1.0,
                u'duration_end':
                u'2013-02-05T15:46:09',
                u'duration': 1734.0,
                u'avg': 1.0,
                u'sum': 135.0,
            }]
        ),
    }
}


class StatisticsManagerTest(unittest.TestCase):

    def setUp(self):
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ceilometerclient.v2.statistics.StatisticsManager(self.api)

    def test_list_by_meter_name(self):
        stats = list(self.mgr.list(meter_name='instance'))
        expect = [
            ('GET', '/v2/meters/instance/statistics', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
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
            ('GET',
             '%s?%s' % (base_url, args), {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(stats), 1)
        self.assertEqual(stats[0].count, 135)
