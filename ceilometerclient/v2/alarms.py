# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc
#
# Author:  Eoghan Glynn <eglynn@redhat.com>
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

import warnings

from ceilometerclient.common import base
from ceilometerclient.common import utils
from ceilometerclient.v2 import options


UPDATABLE_ATTRIBUTES = [
    'name',
    'description',
    'type',
    'state',
    'enabled',
    'alarm_actions',
    'ok_actions',
    'insufficient_data_actions',
    'repeat_actions',
    'threshold_rule',
    'combination_rule',
]
CREATION_ATTRIBUTES = UPDATABLE_ATTRIBUTES + ['project_id', 'user_id']


class Alarm(base.Resource):
    def __repr__(self):
        return "<Alarm %s>" % self._info

    def __getattr__(self, k):
        # Alias to have the Alarm client object
        # that look like the Alarm storage object
        if k == 'rule':
            k = '%s_rule' % self.type
        return super(Alarm, self).__getattr__(k)


class AlarmChange(base.Resource):
    def __repr__(self):
        return "<AlarmChange %s>" % self._info

    def __getattr__(self, k):
        return super(AlarmChange, self).__getattr__(k)


class AlarmManager(base.Manager):
    resource_class = Alarm

    @staticmethod
    def _path(id=None):
        return '/v2/alarms/%s' % id if id else '/v2/alarms'

    def list(self, q=None):
        return self._list(options.build_url(self._path(), q))

    def get(self, alarm_id):
        try:
            return self._list(self._path(alarm_id), expect_single=True)[0]
        except IndexError:
            return None

    @classmethod
    def _compat_legacy_alarm_kwargs(cls, kwargs, create=False):
        cls._compat_counter_rename_kwargs(kwargs, create)
        cls._compat_alarm_before_rule_type_kwargs(kwargs, create)

    @staticmethod
    def _compat_counter_rename_kwargs(kwargs, create=False):
        # NOTE(jd) Compatibility with Havana-2 API
        if 'counter_name' in kwargs:
            warnings.warn("counter_name has been renamed to meter_name",
                          DeprecationWarning)
            kwargs['meter_name'] = kwargs['counter_name']

    @staticmethod
    def _compat_alarm_before_rule_type_kwargs(kwargs, create=False):
        # NOTE(sileht) Compatibility with Havana-3 API
        if create and 'type' not in kwargs:
            warnings.warn("alarm without type set is deprecated",
                          DeprecationWarning)
            kwargs['type'] = 'threshold'

        for field in ['period', 'evaluation_periods', 'threshold',
                      'statistic', 'comparison_operator', 'meter_name']:
            if field in kwargs:
                kwargs.setdefault('threshold_rule', {})[field] = kwargs[field]
                del kwargs[field]

        if 'matching_metadata' in kwargs:
            query = []
            for key in kwargs['matching_metadata']:
                query.append({'field': key,
                              'op': 'eq',
                              'value': kwargs['matching_metadata'][key]})
            del kwargs['matching_metadata']
            kwargs['threshold_rule']['query'] = query

    def create(self, **kwargs):
        self._compat_legacy_alarm_kwargs(kwargs, create=True)
        new = dict((key, value) for (key, value) in kwargs.items()
                   if key in CREATION_ATTRIBUTES)
        return self._create(self._path(), new)

    def update(self, alarm_id, **kwargs):
        self._compat_legacy_alarm_kwargs(kwargs)
        updated = self.get(alarm_id).to_dict()
        kwargs = dict((k, v) for k, v in kwargs.items()
                      if k in updated and k in UPDATABLE_ATTRIBUTES)
        utils.merge_nested_dict(updated, kwargs, depth=1)
        return self._update(self._path(alarm_id), updated)

    def delete(self, alarm_id):
        return self._delete(self._path(alarm_id))

    def set_state(self, alarm_id, state):
        resp, body = self.api.json_request('PUT',
                                           "%s/state" % self._path(alarm_id),
                                           body=state)
        return body

    def get_state(self, alarm_id):
        resp, body = self.api.json_request('GET',
                                           "%s/state" % self._path(alarm_id))
        return body

    def get_history(self, alarm_id, q=None):
        path = '%s/history' % self._path(alarm_id)
        url = options.build_url(path, q)
        return self._list(url, obj_class=AlarmChange)
