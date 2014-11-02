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


class OldSample(base.Resource):
    """Represents API v2 OldSample object.

    Model definition:
    http://docs.openstack.org/developer/ceilometer/webapi/v2.html#OldSample
    """
    def __repr__(self):
        return "<OldSample %s>" % self._info


class OldSampleManager(base.Manager):
    resource_class = OldSample

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
        body = self.api.post(url, json=[new]).json()
        if body:
            return [OldSample(self, b) for b in body]


class Sample(base.Resource):
    """Represents API v2 Sample object.

    Model definition:
    http://docs.openstack.org/developer/ceilometer/webapi/v2.html#Sample
    """
    def __repr__(self):
        return "<Sample %s>" % self._info


class SampleManager(base.Manager):
    resource_class = Sample

    def list(self, q=None, limit=None):
        params = ['limit=%s' % str(limit)] if limit else None
        return self._list(options.build_url("/v2/samples", q, params))

    def get(self, sample_id):
        path = "/v2/samples/" + sample_id
        try:
            return self._list(path, expect_single=True)[0]
        except IndexError:
            return None
