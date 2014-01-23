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

from keystoneclient.v2_0 import client as ksclient

from ceilometerclient.common import utils
from ceilometerclient.openstack.common.apiclient import auth
from ceilometerclient.openstack.common.apiclient import exceptions


class AuthPlugin(auth.BaseAuthPlugin):
    opt_names = ['tenant_id', 'region_name', 'token',
                 'service_type', 'endpoint_type', 'cacert']

    def __init__(self, auth_system=None, **kwargs):
        self.opt_names.extend(self.common_opt_names)
        super(AuthPlugin, self).__init__(auth_system=None, **kwargs)

    def _do_authenticate(self, http_client):
        if self.opts.get('token') and self.opts.get('ceilometer_url'):
            token = self.opts.get('token')
            endpoint = self.opts.get('ceilometer_url')
        elif (self.opts.get('username') and
              self.opts.get('password') and
              self.opts.get('auth_url') and
              (self.opts.get('tenant_id') or self.opts.get('tenant_name'))):

            ks_kwargs = {
                'username': self.opts.get('username'),
                'password': self.opts.get('password'),
                'tenant_id': self.opts.get('tenant_id'),
                'tenant_name': self.opts.get('tenant_name'),
                'auth_url': self.opts.get('auth_url'),
                'region_name': self.opts.get('region_name'),
                'service_type': self.opts.get('service_type'),
                'endpoint_type': self.opts.get('endpoint_type'),
                'cacert': self.opts.get('cacert'),
                'insecure': self.opts.get('insecure'),
            }
            _ksclient = _get_ksclient(**ks_kwargs)
            token = ((lambda: self.opts.get('token'))
                     if self.opts.get('token')
                     else (lambda: _ksclient.auth_token))

            endpoint = self.opts.get('ceilometer_url') or \
                _get_endpoint(_ksclient, **ks_kwargs)
        self.opts['token'] = token()
        self.opts['endpoint'] = endpoint

    def token_and_endpoint(self, endpoint_type, service_type):
        return self.opts.get('token'), self.opts.get('endpoint')

    def sufficient_options(self):
        """Check if all required options are present.

        :raises: AuthPluginOptionsMissing
        """
        missing = [opt
                   for opt in self.opt_names
                   if self.opts.get(opt) is None]
        if missing:
            raise exceptions.AuthPluginOptionsMissing(missing)


def _get_ksclient(**kwargs):
    """Get an endpoint and auth token from Keystone.

    :param kwargs: keyword args containing credentials:
            * username: name of user
            * password: user's password
            * auth_url: endpoint to authenticate against
            * cacert: path of CA TLS certificate
            * insecure: allow insecure SSL (no cert verification)
            * tenant_{name|id}: name or ID of tenant
    """
    return ksclient.Client(username=kwargs.get('username'),
                           password=kwargs.get('password'),
                           tenant_id=kwargs.get('tenant_id'),
                           tenant_name=kwargs.get('tenant_name'),
                           auth_url=kwargs.get('auth_url'),
                           region_name=kwargs.get('region_name'),
                           cacert=kwargs.get('cacert'),
                           insecure=kwargs.get('insecure'))


def _get_endpoint(client, **kwargs):
    """Get an endpoint using the provided keystone client."""
    return client.service_catalog.url_for(
        service_type=kwargs.get('service_type') or 'metering',
        endpoint_type=kwargs.get('endpoint_type') or 'publicURL')


def Client(version, *args, **kwargs):
    module = utils.import_versioned_module(version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)
