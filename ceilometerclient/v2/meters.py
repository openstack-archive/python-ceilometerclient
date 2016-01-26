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


class Meter(base.Resource):
    def __repr__(self):
        return "<Meter %s>" % self._info


class MeterManager(base.Manager):
    resource_class = Meter

    def list(self, q=None, limit=None, unique=False):
        path = '/v2/meters'
        params = []

        if limit:
            params.append('limit=%s' % limit)

        if unique:
            params.append('unique=%s' % str(unique))

        return self._list(options.build_url(path, q, params))
