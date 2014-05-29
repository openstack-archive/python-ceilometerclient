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

from keystoneclient.auth.identity import v2 as v2_auth
from keystoneclient.auth.identity import v3 as v3_auth
from keystoneclient import discover
from keystoneclient import session
import six

from ceilometerclient.common import utils
from ceilometerclient import exc
from ceilometerclient.openstack.common import cliutils


def _get_keystone_session(**kwargs):
    # first create a Keystone session 
    cacert = kwargs.pop('cacert', None)
    cert = kwargs.pop('cert', None)
    key = kwargs.pop('key', None)
    insecure = kwargs.pop('insecure', False)
    auth_url = kwargs.pop('auth_url', None)
    
    if insecure:
        verify = False
    else:
        verify = cacert or True

    # create the keystone client session
    ks_session = session.Session(verify=verify, cert=cert)
    
    try:
        # discover the supported keystone versions using the auth endpoint url
        ks_discover = discover.Discover(session=ks_session, auth_url=auth_url)
        # Determine which authentication plugin to use.
        v2_auth_url = ks_discover.url_for('2.0')
        v3_auth_url = ks_discover.url_for('3.0')
    except Exception:
        raise exc.CommandError(
                'Unable to determine the Keystone version '
                'to authenticate with using the given '
                'auth_url: %s' % auth_url)
    
    username = kwargs.pop('username', None)
    user_id = kwargs.pop('user_id', None)
    user_domain_name = kwargs.pop('user_domain_name', None)
    user_domain_id = kwargs.pop('user_domain_id', None)
    auth = None
            
    if v3_auth_url and v2_auth_url:
        #support both v2 and v3 auth. Use v3 if possible.
        if username:
            if user_domain_name or user_domain_id:
                # use v3 auth
                auth = v3_auth.Password(
                    v3_auth_url,
                    username=username,
                    user_id=user_id,
                    user_domain_name=user_domain_name,
                    user_domain_id=user_domain_id,
                    **kwargs)
            else:
                # use v2 auth
                auth = v2_auth.Password(
                    v2_auth_url,
                    username,
                    kwargs.pop('password', None),
                    tenant_id=kwargs.pop('tenant_id', None),
                    tenant_name=kwargs.pop('tenant_name', None))
        elif v3_auth_url and not v2_auth_url:
            # support only v3
            auth = v3_auth.Password(
                v3_auth_url,
                username=username,
                user_id=user_id,
                user_domain_name=user_domain_name,
                user_domain_id=user_domain_id,
                **kwargs)
        elif v2_auth_url and not v3_auth_url:
            # support only v2
            auth = v2_auth.Password(
                v2_auth_url,
                username,
                kwargs.pop('password', None),
                tenant_id=kwargs.pop('tenant_id', None),
                tenant_name=kwargs.pop('tenant_name', None))
        else:
            raise exc.CommandError(
                'Unable to determine the Keystone version '
                'to authenticate with using the given '
                'auth_url.')

    ks_session.auth = auth
    return ks_session


def _get_endpoint(ks_session, **kwargs):
    """Get an endpoint using the provided keystone session."""

    #set service specific endpoint types
    endpoint_type=kwargs.get('endpoint_type') or 'publicURL'
    service_type=kwargs.get('service_type') or 'metering'

    
    endpoint = ks_session.get_endpoint(
            service_type=service_type,
            endpoint_type=endpoint_type,
            region_name=kwargs.get('region_name'))
    
    return endpoint


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
    token = kwargs.get('os_auth_token')
    if token and not six.callable(token):
        token = lambda: kwargs.get('os_auth_token')

    if token and kwargs.get('ceilometer_url'):
        endpoint = kwargs.get('ceilometer_url')
    else:
        ks_kwargs = {
            'username': kwargs.get('os_username'),
            'password': kwargs.get('os_password'),
            'user_id': kwargs.get('os_user_id'),
            'user_domain_id': kwargs.get('os_user_domain_id'),
            'user_domain_name': kwargs.get('os_user_domain_name'),
            'tenant_id': kwargs.get('os_tenant_id'),
            'tenant_name': kwargs.get('os_tenant_name'),
            'project_id': kwargs.get('os_project_id'),
            'project_name': kwargs.get('os_project_name'),
            'project_domain_name': kwargs.get('os_project_domain_name'),
            'project_domain_id': kwargs.get('os_project_domain_id'),
            'auth_url': kwargs.get('os_auth_url'),
            'region_name': kwargs.get('os_region_name'),
            'service_type': kwargs.get('os_service_type'),
            'endpoint_type': kwargs.get('os_endpoint_type'),
            'cacert': kwargs.get('os_cacert'),
            'cert': kwargs.get('os_cert'),
            'insecure': kwargs.get('insecure'),
            'key': kwargs.get('os_key')
        }

        #retrieve session
        ks_session = _get_keystone_session(**ks_kwargs)
        token = token or (lambda: ks_session.get_token())

        endpoint = kwargs.get('ceilometer_url') or \
            _get_endpoint(ks_session, **ks_kwargs)

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
