# Copyright Ericsson AB 2014. All rights reserved
#
# Authors: Balazs Gibizer <balazs.gibizer@ericsson.com>
#          Ildiko Vancsa <ildiko.vancsa@ericsson.com>
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

import six

from ceilometerclient.common import base
from ceilometerclient.v2 import alarms
from ceilometerclient.v2 import samples
from ceilometerclient.v2 import statistics


class QueryManager(base.Manager):
    path_suffix = None

    def _make_query(self, **kwargs):
        query = {}
        for key, value in six.iteritems(kwargs):
            if value:
                query[key] = value

        url = '/v2/query%s' % self.path_suffix

        body = self.api.post(url, json=query).json()

        if body:
            return [self.resource_class(self, b) for b in body]
        else:
            return []


class QueryStatisticsManager(QueryManager):
    path_suffix = '/statistics'
    resource_class = statistics.Statistics

    def query(self, filter=None, period=None, groupby=None, aggregate=None):
        if isinstance(groupby, six.string_types):
            groupby = [groupby]
        return self._make_query(filter=filter, period=period, groupby=groupby,
                         aggregate=aggregate)


class QueryStandardManager(QueryManager):
    def query(self, filter=None, orderby=None, limit=None):
        return self._make_query(filter=filter, orderby=orderby, limit=limit)


class QuerySamplesManager(QueryStandardManager):
    resource_class = samples.Sample
    path_suffix = '/samples'


class QueryAlarmsManager(QueryStandardManager):
    resource_class = alarms.Alarm
    path_suffix = '/alarms'


class QueryAlarmHistoryManager(QueryStandardManager):
    resource_class = alarms.AlarmChange
    path_suffix = '/alarms/history'
