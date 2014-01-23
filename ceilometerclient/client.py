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
                 'service_type', 'endpoint_type', 'cacert',
                 'endpoint', 'insecure', 'cert_file', 'key_file']

    def __init__(self, auth_system=None, **kwargs):
        self.opt_names.extend(self.common_opt_names)
        super(AuthPlugin, self).__init__(auth_system=None, **kwargs)

    def _do_authenticate(self, http_client):
        if self.opts.get('token') and self.opts.get('endpoint'):
            token = self.opts.get('token')
            endpoint = self.opts.get('ceilometer_url')
        else:
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
                'cert_file': self.opts.get('cert_file'),
                'key_file': self.opts.get('key_file'),
            }
            _ksclient = _get_ksclient(**ks_kwargs)
            token = ((lambda: self.opts.get('token'))
                     if self.opts.get('token')
                     else (lambda: _ksclient.auth_token))

            endpoint = self.opts.get('endpoint') or \
                _get_endpoint(_ksclient, **ks_kwargs)
        self.opts['token'] = token()
        self.opts['endpoint'] = endpoint

    def token_and_endpoint(self, endpoint_type, service_type):
        token = self.opts.get('token')
        if callable(token):
            token = token()
        return token, self.opts.get('endpoint')

    def sufficient_options(self):
        """Check if all required options are present.

        :raises: AuthPluginOptionsMissing
        """
        missing = not ((self.opts.get('token') and
                        self.opts.get('endpoint')) or
                       (self.opts.get('username')
                        and self.opts.get('password')
                        and self.opts.get('auth_url') and
                        (self.opts.get('tenant_id')
                        or self.opts.get('tenant_name'))))

        if missing:
            missing_opts = []
            opts = ['token', 'endpoint', 'username', 'password', 'auth_url',
                    'tenant_id', 'tenant_name']
            for opt in opts:
                if not self.opts.get(opt):
                    missing_opts.append(opt)
            raise exceptions.AuthPluginOptionsMissing(missing_opts)


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


def get_client(version, **kwargs):
    """Get an authtenticated client, based on the credentials
    in the keyword args.

    :param api_version: the API version to use ('1' or '2')
    :param kwargs: keyword args containing credentials, either:
    * os_auth_token: pre-existing token to re-use
    * ceilometer_url: ceilometer API endpoint
    or:
    * os_username: name of user
    * os_password: user's password
    * os_auth_url: endpoint to authenticate against
    * os_cacert: path of CA TLS certificate
    * insecure: allow insecure SSL (no cert verification)
    * os_tenant_{name|id}: name or ID of tenant
    """
    endpoint = kwargs.get('ceilometer_url')

    cli_kwargs = {
        'username': kwargs.get('os_username'),
        'password': kwargs.get('os_password'),
        'tenant_id': kwargs.get('os_tenant_id'),
        'tenant_name': kwargs.get('os_tenant_name'),
        'auth_url': kwargs.get('os_auth_url'),
        'region_name': kwargs.get('os_region_name'),
        'service_type': kwargs.get('os_service_type'),
        'endpoint_type': kwargs.get('os_endpoint_type'),
        'cacert': kwargs.get('os_cacert'),
        'token': kwargs.get('os_auth_token'),

    }
    cli_kwargs.update(kwargs)
    return Client(version, endpoint, **cli_kwargs)
