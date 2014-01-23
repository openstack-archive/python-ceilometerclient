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

from ceilometerclient.common import http
from ceilometerclient.openstack.common.apiclient import client
from ceilometerclient.v2 import alarms
from ceilometerclient.v2 import event_types
from ceilometerclient.v2 import events
from ceilometerclient.v2 import meters
from ceilometerclient.v2 import resources
from ceilometerclient.v2 import samples
from ceilometerclient.v2 import statistics
from ceilometerclient.v2 import trait_descriptions
from ceilometerclient.v2 import traits


class Client(object):
    """Client for the Ceilometer v2 API.

    :param string endpoint: A user-supplied endpoint URL for the ceilometer
                            service.
    :param function token: Provides token for authentication.
    :param integer timeout: Allows customization of the timeout for client
                            http requests. (optional)
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Ceilometer v1 API."""
        auth_plugin = kwargs.get('auth_plugin')
        if auth_plugin:
            del kwargs['auth_plugin']
            self.get_common_http_client(auth_plugin, **kwargs)
        else:
            self.client = http.HTTPClient(*args, **kwargs)
            self.http_client = client.BaseClient(self.client)

        self.meters = meters.MeterManager(self.http_client)
        self.samples = samples.SampleManager(self.http_client)
        self.statistics = statistics.StatisticsManager(self.http_client)
        self.resources = resources.ResourceManager(self.http_client)
        self.alarms = alarms.AlarmManager(self.http_client)
        self.events = events.EventManager(self.http_client)
        self.event_types = event_types.EventTypeManager(self.http_client)
        self.traits = traits.TraitManager(self.http_client)
        self.trait_info = trait_descriptions.\
            TraitDescriptionManager(self.http_client)

    def get_common_http_client(self, auth_plugin, **kwargs):
        self.client = client.HTTPClient(auth_plugin,
                                        region_name=kwargs.get('region_name'),
                                        endpoint_type=
                                        kwargs.get('endpoint_type'),
                                        original_ip=kwargs.get('original_ip'),
                                        verify=kwargs.get('verify'),
                                        cert=kwargs.get('cacert'),
                                        timeout=kwargs.get('timeout'),
                                        timings=kwargs.get('timings'),
                                        keyring_saver=
                                        kwargs.get('keyring_saver'),
                                        debug=kwargs.get('debug'),
                                        user_agent=kwargs.get('user_agent'),
                                        http=kwargs.get('http')
                                        )

        self.http_client = client.BaseClient(self.client)
