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

import urllib

from ceilometerclient.common import base


class Sample(base.Resource):
    def __repr__(self):
        return "<Sample %s>" % self._info


class SampleManager(base.Manager):
    resource_class = Sample

    @staticmethod
    def build_url(path, q):
        if q:
            query_params = {'q.field': [],
                            'q.value': [],
                            'q.op': []}

            for query in q:
                for name in ['field', 'op', 'value']:
                    query_params['q.%s' % name].append(query.get(name, ''))

            path += "?" + urllib.urlencode(query_params, doseq=True)

        return path

    def list(self, meter_name=None, q=None):
        path = '/v2/meters'
        if meter_name:
            path += '/' + meter_name
        return self._list(self.build_url(path, q))
