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
from ceilometerclient.v2 import options

CREATION_ATTRIBUTES = ('source',
                       'counter_name',
                       'counter_type',
                       'counter_unit',
                       'counter_volume',
                       'user_id',
                       'project_id',
                       'resource_id',
                       'timestamp',
                       'resource_metadata')


class Sample(base.Resource):
    def __repr__(self):
        return "<Sample %s>" % self._info


class SampleManager(base.Manager):
    resource_class = Sample

    @staticmethod
    def _path(counter_name=None):
        return '/v2/meters/%s' % counter_name if counter_name else '/v2/meters'

    def list(self, meter_name=None, q=None, limit=None):
        path = self._path(counter_name=meter_name)
        params = ['limit=%s' % str(limit)] if limit else None
        return self._list(options.build_url(path, q, params))

    def create(self, **kwargs):
        new = dict((key, value) for (key, value) in kwargs.items()
                   if key in CREATION_ATTRIBUTES)
        url = self._path(counter_name=kwargs['counter_name'])
        resp, body = self.api.json_request('POST',
                                           url,
                                           body=[new])
        if body:
            return [Sample(self, b) for b in body]
