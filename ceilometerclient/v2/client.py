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
from keystoneauth1 import exceptions as ka_exc
from keystoneclient import exceptions as kc_exc


class Client(object):
    """Client for the Ceilometer v2 API.

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
        """Initialize a new client for the Ceilometer v2 API."""

        if not kwargs.get('auth_plugin') and not kwargs.get('session'):
            kwargs['auth_plugin'] = ceiloclient.get_auth_plugin(*args,
                                                                **kwargs)

        self.auth_plugin = kwargs.get('auth_plugin')

        self.http_client = ceiloclient._construct_http_client(**kwargs)
        self.alarm_client = self._get_alarm_client(**kwargs)
        aodh_enabled = self.alarm_client is not None
        if not aodh_enabled:
            self.alarm_client = self.http_client
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

    @staticmethod
    def _get_alarm_client(**ceilo_kwargs):
        """Get client for alarm manager that redirect to aodh."""
        # NOTE(sileht): the auth_plugin/keystone session cannot be copied
        # because they rely on threading module.
        auth_plugin = ceilo_kwargs.pop('auth_plugin', None)
        session = ceilo_kwargs.pop('session', None)

        kwargs = copy.deepcopy(ceilo_kwargs)
        kwargs["service_type"] = "alarming"
        aodh_endpoint = ceilo_kwargs.get('aodh_endpoint')

        if session:
            # keystone session can be shared between client
            ceilo_kwargs['session'] = kwargs['session'] = session
            if aodh_endpoint:
                kwargs['endpoint_override'] = aodh_endpoint
        elif auth_plugin and kwargs.get('auth_url'):
            ceilo_kwargs['auth_plugin'] = auth_plugin
            kwargs.pop('endpoint', None)
            kwargs['auth_plugin'] = ceiloclient.get_auth_plugin(
                aodh_endpoint, **kwargs)
        else:
            # Users may just provided ceilometer endpoint and token, and no
            # auth_url, in this case, we need 'aodh_endpoint' also
            # provided, otherwise we cannot get aodh endpoint from
            # keystone, and assume aodh is unavailable.
            return None

        try:
            # NOTE(sileht): try to use aodh
            c = ceiloclient._construct_http_client(**kwargs)
            c.get("/")
            return c
        except ka_exc.EndpointNotFound:
            return None
        except kc_exc.EndpointNotFound:
            return None
