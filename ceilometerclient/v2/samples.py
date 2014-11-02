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

    def list(self, meter_name=None, q=None, limit=None):
        if meter_name:
            path = '/v2/meters/' + meter_name
        else:
            path = '/v2/samples'
        params = ['limit=%s' % limit] if limit else None
        return self._list(options.build_url(path, q, params))

    def get(self, sample_id):
        path = '/v2/samples/' + sample_id
        body = self.api.get(path).json()
        if body:
            return Sample(self, body)

    def create(self, **kwargs):
        new = dict((key, value) for (key, value) in kwargs.items()
                   if key in CREATION_ATTRIBUTES)
        url = '/v2/meters/' + kwargs['counter_name']
        body = self.api.post(url, json=[new]).json()
        if body:
            return [Sample(self, b) for b in body]
