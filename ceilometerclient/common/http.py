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

import copy
import logging
import os
import socket

try:
    import json
except ImportError:
    import simplejson as json

import requests
import six
from six.moves import http_client as httplib  # noqa

from ceilometerclient import exc
from ceilometerclient.openstack.common.py3kcompat import urlutils


LOG = logging.getLogger(__name__)
USER_AGENT = 'python-ceilometerclient'
CHUNKSIZE = 1024 * 64  # 64kB


def get_system_ca_file():
    """Return path to system default CA file."""
    # Standard CA file locations for Debian/Ubuntu, RedHat/Fedora,
    # Suse, FreeBSD/OpenBSD
    ca_path = ['/etc/ssl/certs/ca-certificates.crt',
               '/etc/pki/tls/certs/ca-bundle.crt',
               '/etc/ssl/ca-bundle.pem',
               '/etc/ssl/cert.pem']
    for ca in ca_path:
        if os.path.exists(ca):
            return ca
    return None


class HTTPClient(object):

    def __init__(self, endpoint, **kwargs):
        self.endpoint = endpoint
        self.auth_token = kwargs.get('token')
        self.proxy_url = self.get_proxy_url()
        self.endpoint_url = endpoint
        self.cert_file = kwargs.get('cert_file')
        self.key_file = kwargs.get('key_file')
        self.verify_cert = None
        if endpoint.startswith("https"):
            if kwargs.get('insecure'):
                self.verify_cert = False
            else:
                self.verify_cert = kwargs.get('ca_file', get_system_ca_file())

    def log_curl_request(self, method, url, kwargs):
        curl = ['curl -i -X %s' % method]

        for (key, value) in kwargs['headers'].items():
            header = '-H \'%s: %s\'' % (key, value)
            curl.append(header)

        if 'body' in kwargs:
            curl.append('-d \'%s\'' % kwargs['body'])

        curl.append('%s/%s' % (self.endpoint.rstrip('/'), url.lstrip('/')))
        LOG.debug(' '.join(curl))

    @staticmethod
    def log_http_response(resp, data=None):
        status = (resp.raw.version / 10.0, resp.status_code, resp.reason)
        dump = ['\nHTTP/%.1f %s %s' % status]
        dump.extend(['%s: %s' % (k, v) for k, v in resp.headers.items()])
        dump.append('')
        if data:
            dump.extend([data, ''])
        LOG.debug('\n'.join(dump))

    def _make_connection_url(self, url):
        return '%s/%s' % (self.endpoint_url.rstrip('/'), url.lstrip('/'))

    def _http_request(self, url, method, **kwargs):
        """Send an http request with the specified characteristics.

        Wrapper around requests.request to handle tasks such
        as setting headers and error handling.
        """
        # Copy the kwargs so we can reuse the original in case of redirects
        kwargs['headers'] = copy.deepcopy(kwargs.get('headers', {}))
        kwargs['headers'].setdefault('User-Agent', USER_AGENT)
        auth_token = self.auth_token()
        if auth_token:
            kwargs['headers'].setdefault('X-Auth-Token', auth_token)

        self.log_curl_request(method, url, kwargs)

        if self.cert_file and self.key_file:
            kwargs['cert'] = (self.cert_file, self.key_file)

        if self.verify_cert is not None:
            kwargs['verify'] = self.verify_cert

        # We are not using requests builtin redirection on DELETE since it does
        # not follow the RFC having to resend the same method on a
        # redirect. For example if we do a DELETE on a URL and we get
        # a 302 RFC says that we should follow that URL with the same
        # method as before, requests doesn't follow that and send a
        # GET instead for the method.  See issue:
        # https://github.com/kennethreitz/requests/issues/1704
        # hopefully this could be fixed as they say in a comment in a
        # future point version i.e: 3.x
        if method == 'DELETE':
            allow_redirects = False
        else:
            allow_redirects = True

        try:
            if self.proxy_url:
                conn_url = self.endpoint + self._make_connection_url(url)
            else:
                conn_url = self._make_connection_url(url)
            resp = requests.request(
                method,
                conn_url,
                allow_redirects=allow_redirects,
                **kwargs)
        except socket.gaierror as e:
            message = ("Error finding address for %(url)s: %(e)s"
                       % dict(url=url, e=e))
            raise exc.InvalidEndpoint(message=message)
        except (socket.error, socket.timeout) as e:
            endpoint = self.endpoint
            message = ("Error communicating with %(endpoint)s %(e)s"
                       % dict(endpoint=endpoint, e=e))
            raise exc.CommunicationError(message=message)

        body_iter = resp.iter_content(CHUNKSIZE)

        # Read body into string if it isn't obviously image data
        if resp.headers.get('content-type') != 'application/octet-stream':
            body_str = ''.join([chunk for chunk in body_iter])
            self.log_http_response(resp, body_str)
            body_iter = six.StringIO(body_str)
        else:
            self.log_http_response(resp)

        if 400 <= resp.status_code < 600:
            LOG.warn("Request returned failure status_code.")
            raise exc.from_response(resp, ''.join(body_iter))
        elif resp.status_code in (301, 302, 305):
            # Redirected. Reissue the request to the new location.
            location = resp.headers.get('location')
            if location is None:
                message = "Location not returned with 302"
                raise exc.InvalidEndpoint(message=message)
            return self._http_request(location, method, **kwargs)
        elif resp.status_code == 300:
            raise exc.from_response(resp)

        return resp, body_iter

    def json_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type', 'application/json')
        kwargs['headers'].setdefault('Accept', 'application/json')

        if 'data' in kwargs:
            kwargs['data'] = json.dumps(kwargs['data'])

        resp, body_iter = self._http_request(url, method, **kwargs)
        content_type = resp.headers.get('content-type')

        if any([resp.status_code == 204, resp.status_code == 205,
                content_type is None]):
            return resp, list()

        if 'application/json' in content_type:
            try:
                body = resp.json()
            except ValueError:
                LOG.error('Could not decode response body as JSON')
        else:
            body = None

        return resp, body

    def raw_request(self, method, url, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault('Content-Type',
                                     'application/octet-stream')
        return self._http_request(url, method, **kwargs)

    def get_proxy_url(self):
        scheme = urlutils.urlparse(self.endpoint).scheme
        if scheme == 'https':
            return os.environ.get('https_proxy')
        elif scheme == 'http':
            return os.environ.get('http_proxy')
        msg = 'Unsupported scheme: %s' % scheme
        raise exc.InvalidEndpoint(msg)
