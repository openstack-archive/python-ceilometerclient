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
from ceilometerclient.v2 import samples


class QuerySamplesManager(base.Manager):
    resource_class = samples.Sample

    @staticmethod
    def _path():
        return '/v2/query/samples'

    def query(self, filter, orderby, limit):
        query = {}
        if filter:
            query["filter"] = filter
        if orderby:
            query["orderby"] = orderby
        if limit:
            query["limit"] = limit

        url = self._path()
        resp, body = self.api.json_request('POST',
                                           url,
                                           body=query)
        if body:
            return [self.resource_class(self, b) for b in body]
        else:
            return []
