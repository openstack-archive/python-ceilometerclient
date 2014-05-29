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


def _get_keystone_session(**kwargs):
    # TODO(fabgia): the heavy lifting here should be really done by Keystone.
    # Unfortunately Keystone does not support a richer method to perform
    # discovery and return a single viable URL. A bug against Keystone has
    # been filed: https://bugs.launchpad.net/pyhton-keystoneclient/+bug/1330677

    # first create a Keystone session
    cacert = kwargs.pop('cacert', None)
    cert = kwargs.pop('cert', None)
    key = kwargs.pop('key', None)
    insecure = kwargs.pop('insecure', False)
    auth_url = kwargs.pop('auth_url', None)
    project_id = kwargs.pop('project_id', None)
    project_name = kwargs.pop('project_name', None)

    if insecure:
        verify = False
    else:
        verify = cacert or True

    if cert and key:
        # passing cert and key together is deprecated in favour of the
        # requests lib form of having the cert and key as a tuple
        cert = (cert, key)

    # create the keystone client session
    ks_session = session.Session(verify=verify, cert=cert)

    try:
        # discover the supported keystone versions using the auth endpoint url
        ks_discover = discover.Discover(session=ks_session, auth_url=auth_url)
        # Determine which authentication plugin to use.
        v2_auth_url = ks_discover.url_for('2.0')
        v3_auth_url = ks_discover.url_for('3.0')
    except Exception:
        raise exc.CommandError('Unable to determine the Keystone version '
                               'to authenticate with using the given '
                               'auth_url: %s' % auth_url)

    username = kwargs.pop('username', None)
    user_id = kwargs.pop('user_id', None)
    user_domain_name = kwargs.pop('user_domain_name', None)
    user_domain_id = kwargs.pop('user_domain_id', None)
    project_domain_name = kwargs.pop('project_domain_name', None)
    project_domain_id = kwargs.pop('project_domain_id', None)
    auth = None

    if v3_auth_url and v2_auth_url:
        # the auth_url does not have the versions specified
        # e.g. http://no.where:5000
        # Keystone will return both v2 and v3 as viable options
        # but we need to decide based on the arguments passed
        # what version is callable
        if (user_domain_name or user_domain_id or project_domain_name or
                project_domain_id):
            # domain is supported only in v3
            auth = v3_auth.Password(
                v3_auth_url,
                username=username,
                user_id=user_id,
                user_domain_name=user_domain_name,
                user_domain_id=user_domain_id,
                project_domain_name=project_domain_name,
                project_domain_id=project_domain_id,
                **kwargs)
        else:
            # no domain, then use v2
            auth = v2_auth.Password(
                v2_auth_url,
                username,
                kwargs.pop('password', None),
                tenant_id=project_id,
                tenant_name=project_name)
    elif v3_auth_url:
        # the auth_url as v3 specified
        # e.g. http://no.where:5000/v3
        # Keystone will return only v3 as viable option
        auth = v3_auth.Password(
            v3_auth_url,
            username=username,
            user_id=user_id,
            user_domain_name=user_domain_name,
            user_domain_id=user_domain_id,
            project_domain_name=project_domain_name,
            project_domain_id=project_domain_id,
            **kwargs)
    elif v2_auth_url:
        # the auth_url as v2 specified
        # e.g. http://no.where:5000/v2.0
        # Keystone will return only v2 as viable option
        auth = v2_auth.Password(
            v2_auth_url,
            username,
            kwargs.pop('password', None),
            tenant_id=project_id,
            tenant_name=project_name)
    else:
        raise exc.CommandError('Unable to determine the Keystone version '
                               'to authenticate with using the given '
                               'auth_url.')

    ks_session.auth = auth
    return ks_session


def _get_endpoint(ks_session, **kwargs):
    """Get an endpoint using the provided keystone session."""

    # set service specific endpoint types
    endpoint_type = kwargs.get('endpoint_type') or 'publicURL'
    service_type = kwargs.get('service_type') or 'metering'

    endpoint = ks_session.get_endpoint(service_type=service_type,
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
            * os_user_id: user's id
            * os_user_domain_id: the domain id of the user
            * os_user_domain_name: the domain name of the user
            * os_project_id: the user project id
            * os_tenant_id: V2 alternative to os_project_id
            * os_project_name: the user project name
            * os_tenant_name: V2 alternative to os_project_name
            * os_project_domain_name: domain name for the user project
            * os_project_domain_id: domain id for the user project
            * os_auth_url: endpoint to authenticate against
            * os_cert|os_cacert: path of CA TLS certificate
            * os_key: SSL private key
            * insecure: allow insecure SSL (no cert verification)
    """
    token = kwargs.get('os_auth_token')
    if token and not six.callable(token):
        token = lambda: kwargs.get('os_auth_token')

    if token and kwargs.get('ceilometer_url'):
        endpoint = kwargs.get('ceilometer_url')
    else:
        project_id = kwargs.get('os_project_id') or kwargs.get('os_tenant_id')
        project_name = (kwargs.get('os_project_name') or
                        kwargs.get('os_tenant_name'))
        ks_kwargs = {
            'username': kwargs.get('os_username'),
            'password': kwargs.get('os_password'),
            'user_id': kwargs.get('os_user_id'),
            'user_domain_id': kwargs.get('os_user_domain_id'),
            'user_domain_name': kwargs.get('os_user_domain_name'),
            'project_id': project_id,
            'project_name': project_name,
            'project_domain_name': kwargs.get('os_project_domain_name'),
            'project_domain_id': kwargs.get('os_project_domain_id'),
            'auth_url': kwargs.get('os_auth_url'),
            'cacert': kwargs.get('os_cacert'),
            'cert': kwargs.get('os_cert'),
            'key': kwargs.get('os_key'),
            'insecure': kwargs.get('insecure')
        }

        # retrieve session
        ks_session = _get_keystone_session(**ks_kwargs)
        token = token or (lambda: ks_session.get_token())

        endpoint = kwargs.get('ceilometer_url') or \
            _get_endpoint(ks_session, **ks_kwargs)

    cli_kwargs = {
        'token': token,
        'insecure': kwargs.get('insecure'),
        'timeout': kwargs.get('timeout'),
        'cacert': kwargs.get('os_cacert'),
        'cert': kwargs.get('os_cert'),
        'key': kwargs.get('os_key')
    }

    return Client(api_version, endpoint, **cli_kwargs)


def Client(version, *args, **kwargs):
    module = utils.import_versioned_module(version, 'client')
    client_class = getattr(module, 'Client')
    return client_class(*args, **kwargs)
