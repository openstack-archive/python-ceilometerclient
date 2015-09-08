#
# Copyright 2013 Red Hat, Inc
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


class Resource(base.Resource):
    def __repr__(self):
        return "<Resource %s>" % self._info

    def __getattr__(self, k):
        if k == 'id':
            return self.resource_id
        return super(Resource, self).__getattr__(k)


class ResourceManager(base.Manager):
    resource_class = Resource

    def list(self, q=None, links=None, limit=None):
        path = '/v2/resources'
        params = ['meter_links=%d' % (1 if links else 0)]
        if limit:
            params.append('limit=%s' % limit)
        return self._list(options.build_url(path, q, params))

    def get(self, resource_id):
        path = '/v2/resources/%s' % resource_id
        try:
            return self._list(path, expect_single=True)[0]
        except IndexError:
            return None
