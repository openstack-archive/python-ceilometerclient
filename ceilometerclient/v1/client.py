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
from ceilometerclient.openstack.common.apiclient import client
from ceilometerclient.v1 import meters


class Client(object):
    """Client for the Ceilometer v1 API.

    :param string endpoint: A user-supplied endpoint URL for the ceilometer
                            service.
    :param function token: Provides token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Ceilometer v1 API."""
        self.auth_plugin = kwargs.get('auth_plugin') \
            or ceiloclient.get_auth_plugin(*args, **kwargs)
        self.client = client.HTTPClient(
            auth_plugin=self.auth_plugin,
            region_name=kwargs.get('region_name'),
            endpoint_type=kwargs.get('endpoint_type'),
            original_ip=kwargs.get('original_ip'),
            verify=kwargs.get('verify'),
            cert=kwargs.get('cert'),
            timeout=kwargs.get('timeout'),
            timings=kwargs.get('timings'),
            keyring_saver=kwargs.get('keyring_saver'),
            debug=kwargs.get('debug'),
            user_agent=kwargs.get('user_agent'),
            http=kwargs.get('http')
        )

        self.http_client = client.BaseClient(self.client)
        self.meters = meters.MeterManager(self.http_client)
        self.samples = meters.SampleManager(self.http_client)
        self.users = meters.UserManager(self.http_client)
        self.resources = meters.ResourceManager(self.http_client)
        self.projects = meters.ProjectManager(self.http_client)
