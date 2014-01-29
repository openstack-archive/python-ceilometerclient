# Copyright 2012 OpenStack Foundation
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

"""
Base utilities to build API operation managers and objects on top of.
"""

import copy

from ceilometerclient.openstack.common.apiclient import base

# Python 2.4 compat
try:
    all
except NameError:
    def all(iterable):
        return True not in (not x for x in iterable)


def getid(obj):
    """Abstracts the common pattern of allowing both an object or an
    object's ID (UUID) as a parameter when dealing with relationships.
    """
    try:
        return obj.id
    except AttributeError:
        return obj


class Manager(object):
    """Managers interact with a particular type of API
    (samples, meters, alarms, etc.) and provide CRUD operations for them.
    """
    resource_class = None

    def __init__(self, api):
        self.api = api

    def _create(self, url, body):
        resp = self.api.post(url, json=body).json()
        if resp:
            return self.resource_class(self, resp)

    def _list(self, url, response_key=None, obj_class=None, body=None,
              expect_single=False):
        resp = self.api.get(url).json()

        if obj_class is None:
            obj_class = self.resource_class

        if response_key:
            try:
                data = resp[response_key]
            except KeyError:
                return []
        else:
            data = resp
        if expect_single:
            data = [data]
        return [obj_class(self, res, loaded=True) for res in data if res]

    def _update(self, url, body, response_key=None):
        resp = self.api.put(url, json=body).json()
        # PUT requests may not return a body
        if resp:
            return self.resource_class(self, resp)

    def _delete(self, url):
        self.api.delete(url)


class Resource(base.Resource):
    """A resource represents a particular instance of an object (tenant, user,
    etc). This is pretty much just a bag for attributes.

    :param manager: Manager object
    :param info: dictionary representing resource attributes
    :param loaded: prevent lazy-loading if set to True
    """

    def to_dict(self):
        return copy.deepcopy(self._info)
