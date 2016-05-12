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

from ceilometerclient.common import base
from ceilometerclient.v2 import alarms
from ceilometerclient.v2 import samples


class QueryManager(base.Manager):
    path_suffix = None

    def query(self, filter=None, orderby=None, limit=None):
        query = {}
        if filter:
            query["filter"] = filter
        if orderby:
            query["orderby"] = orderby
        if limit:
            query["limit"] = limit

        url = '/v2/query%s' % self.path_suffix

        body = self.api.post(url, json=query).json()

        if body:
            return [self.resource_class(self, b) for b in body]
        else:
            return []


class QuerySamplesManager(QueryManager):
    resource_class = samples.Sample
    path_suffix = '/samples'


class QueryAlarmsManager(QueryManager):
    resource_class = alarms.Alarm
    path_suffix = '/alarms'


class QueryAlarmHistoryManager(QueryManager):
    resource_class = alarms.AlarmChange
    path_suffix = '/alarms/history'
