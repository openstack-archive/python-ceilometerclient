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


from ceilometerclient import client as ceiloclient
from ceilometerclient.v1 import meters


class Client(object):
    """Client for the Ceilometer v1 API.

    :param session: a keystoneauth/keystoneclient session object
    :type session: keystoneclient.session.Session
    :param str service_type: The default service_type for URL discovery
    :param str service_name: The default service_name for URL discovery
    :param str interface: The default interface for URL discovery
                          (Default: public)
    :param str region_name: The default region_name for URL discovery
    :param str endpoint_override: Always use this endpoint URL for requests
                                  for this ceiloclient
    :param auth: An auth plugin to use instead of the session one
    :type auth: keystoneclient.auth.base.BaseAuthPlugin
    :param str user_agent: The User-Agent string to set
                           (Default is python-ceilometer-client)
    :param int connect_retries: the maximum number of retries that should be
                                attempted for connection errors
    :param logger: A logging object
    :type logger: logging.Logger
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Ceilometer v1 API."""

        if not kwargs.get('auth_plugin'):
            kwargs['auth_plugin'] = ceiloclient.get_auth_plugin(*args,
                                                                **kwargs)
        self.auth_plugin = kwargs.get('auth_plugin')

        self.http_client = ceiloclient._construct_http_client(**kwargs)
        self.meters = meters.MeterManager(self.http_client)
        self.samples = meters.SampleManager(self.http_client)
        self.users = meters.UserManager(self.http_client)
        self.resources = meters.ResourceManager(self.http_client)
        self.projects = meters.ProjectManager(self.http_client)
