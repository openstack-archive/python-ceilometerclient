# Copyright Ericsson AB 2014. All rights reserved
#
# Authors: Balazs Gibizer <balazs.gibizer@ericsson.com>
#          Ildiko Vancsa <ildiko.vancsa@ericsson.com>
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
import copy

from ceilometerclient import client as ceiloclient
from ceilometerclient.openstack.common.apiclient import client
from ceilometerclient.v2 import alarms
from ceilometerclient.v2 import capabilities
from ceilometerclient.v2 import event_types
from ceilometerclient.v2 import events
from ceilometerclient.v2 import meters
from ceilometerclient.v2 import query
from ceilometerclient.v2 import resources
from ceilometerclient.v2 import samples
from ceilometerclient.v2 import statistics
from ceilometerclient.v2 import trait_descriptions
from ceilometerclient.v2 import traits
from keystoneclient import exceptions


class Client(object):
    """Client for the Ceilometer v2 API.

    :param endpoint: A user-supplied endpoint URL for the ceilometer
                            service.
    :type endpoint: string
    :param token: Provides token for authentication.
    :type token: function
    :param timeout: Allows customization of the timeout for client
                    http requests. (optional)
    :type timeout: integer
    """

    def __init__(self, *args, **kwargs):
        """Initialize a new client for the Ceilometer v2 API."""
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
        self.alarm_client, aodh_enabled = self._get_alarm_client(**kwargs)
        self.meters = meters.MeterManager(self.http_client)
        self.samples = samples.OldSampleManager(self.http_client)
        self.new_samples = samples.SampleManager(self.http_client)
        self.statistics = statistics.StatisticsManager(self.http_client)
        self.resources = resources.ResourceManager(self.http_client)
        self.alarms = alarms.AlarmManager(self.alarm_client, aodh_enabled)
        self.events = events.EventManager(self.http_client)
        self.event_types = event_types.EventTypeManager(self.http_client)
        self.traits = traits.TraitManager(self.http_client)
        self.trait_descriptions = trait_descriptions.\
            TraitDescriptionManager(self.http_client)

        self.query_samples = query.QuerySamplesManager(
            self.http_client)
        self.query_alarms = query.QueryAlarmsManager(self.alarm_client)
        self.query_alarm_history = query.QueryAlarmHistoryManager(
            self.alarm_client)
        self.capabilities = capabilities.CapabilitiesManager(self.http_client)

    def _get_alarm_client(self, **kwargs):
        """Get client for alarm manager that redirect to aodh."""

        self.alarm_auth_plugin = copy.deepcopy(self.auth_plugin)
        aodh_endpoint = kwargs.get('aodh_endpoint')
        if aodh_endpoint:
            self.alarm_auth_plugin.opts['endpoint'] = aodh_endpoint
        elif not kwargs.get('auth_url'):
            # Users may just provided ceilometer endpoint and token, and no
            # auth_url, in this case, we need 'aodh_endpoint' also provided,
            # otherwise we cannot get aodh endpoint from keystone, and assume
            # aodh is unavailable.
            return self.http_client, False
        else:
            try:
                # NOTE(liusheng): Getting the aodh's endpoint to rewrite
                # the endpoint of alarm auth_plugin.
                self.alarm_auth_plugin.redirect_to_aodh_endpoint(
                    kwargs.get('timeout'))
            except exceptions.EndpointNotFound:
                return self.http_client, False
        alarm_client = client.HTTPClient(
            auth_plugin=self.alarm_auth_plugin,
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
        return client.BaseClient(alarm_client), True
