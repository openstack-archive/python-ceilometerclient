# Copyright 2014 Hewlett-Packard Development Company, L.P.
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


class Event(base.Resource):
    def __repr__(self):
        return "<Event %s>" % self._info

    def __getattr__(self, k):
        if k == 'id':
            return self.message_id
        return super(Event, self).__getattr__(k)


class EventManager(base.Manager):
    resource_class = Event

    def list(self, q=None, limit=None):
        path = '/v2/events'
        params = ['limit=%s' % limit] if limit else None
        return self._list(options.build_url(path, q, params))

    def get(self, message_id):
        path = '/v2/events/%s'
        try:
            return self._list(path % message_id, expect_single=True)[0]
        except IndexError:
            return None
