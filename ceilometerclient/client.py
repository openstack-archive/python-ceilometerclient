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

from ceilometerclient.common import utils
from keystoneclient.v2_0 import client as ksclient


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


def get_client(api_version, **kwargs):
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
    if kwargs.get('os_auth_token') and kwargs.get('ceilometer_url'):
        token = kwargs.get('os_auth_token')
        endpoint = kwargs.get('ceilometer_url')
    elif (kwargs.get('os_username') and
          kwargs.get('os_password') and
          kwargs.get('os_auth_url') and
          (kwargs.get('os_tenant_id') or kwargs.get('os_tenant_name'))):

        ks_kwargs = {
            'username': kwargs.get('os_username'),
            'password': kwargs.get('os_password'),
            'tenant_id': kwargs.get('os_tenant_id'),
            'tenant_name': kwargs.get('os_tenant_name'),
            'auth_url': kwargs.get('os_auth_url'),
            'region_name': kwargs.get('os_region_name'),
            'service_type': kwargs.get('os_service_type'),
            'endpoint_type': kwargs.get('os_endpoint_type'),
            'cacert': kwargs.get('os_cacert'),
            'insecure': kwargs.get('insecure'),
        }
        _ksclient = _get_ksclient(**ks_kwargs)
        token = ((lambda: kwargs.get('os_auth_token'))
                 if kwargs.get('os_auth_token')
                 else (lambda: _ksclient.auth_token))

        endpoint = kwargs.get('ceilometer_url') or \
            _get_endpoint(_ksclient, **ks_kwargs)

    cli_kwargs = {
        'token': token,
        'insecure': kwargs.get('insecure'),
        'timeout': kwargs.get('timeout'),
        'cacert': kwargs.get('os_cacert'),
        'cert_file': kwargs.get('cert_file'),
        'key_file': kwargs.get('key_file'),
    }

    return Client(api_version, endpoint, **cli_kwargs)


def Client(version, *args, **kwargs):
    module = utils.import_versioned_module(version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)
