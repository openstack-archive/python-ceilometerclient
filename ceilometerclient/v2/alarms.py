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
from ceilometerclient.v2 import options


UPDATABLE_ATTRIBUTES = [
    'description',
    'period',
    'evaluation_periods',
    'state',
    'enabled',
    'meter_name',
    'statistic',
    'comparison_operator',
    'threshold',
    'alarm_actions',
    'ok_actions',
    'insufficient_data_actions',
    'repeat_actions',
    'matching_metadata',
    ]
CREATION_ATTRIBUTES = UPDATABLE_ATTRIBUTES + ['name', 'project_id', 'user_id']


class Alarm(base.Resource):
    def __repr__(self):
        return "<Alarm %s>" % self._info


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

    @staticmethod
    def _compat_counter_rename_kwargs(kwargs):
        # NOTE(jd) Compatibility with Havana-2 API
        if 'counter_name' in kwargs:
            warnings.warn("counter_name has been renamed to meter_name",
                          DeprecationWarning)
            kwargs['meter_name'] = kwargs['counter_name']

    def create(self, **kwargs):
        self._compat_counter_rename_kwargs(kwargs)
        new = dict((key, value) for (key, value) in kwargs.items()
                   if key in CREATION_ATTRIBUTES)
        return self._create(self._path(), new)

    def update(self, alarm_id, **kwargs):
        self._compat_counter_rename_kwargs(kwargs)
        updated = dict((key, value) for (key, value) in kwargs.items()
                       if key in UPDATABLE_ATTRIBUTES)
        return self._update(self._path(alarm_id), updated)

    def delete(self, alarm_id):
        return self._delete(self._path(alarm_id))
