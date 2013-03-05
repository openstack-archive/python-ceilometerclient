import mock
import requests
import mox
import httplib
import StringIO
import socket

from ceilometerclient.common import http
from ceilometerclient import exc
from tests import utils
from testtools.matchers import Contains

class TestClient(utils.TestCase):

    def setUp(self):
        super(TestClient, self).setUp()
        self.mock = mox.Mox()
        self.mock.StubOutWithMock(httplib.HTTPConnection, 'request')
        self.mock.StubOutWithMock(httplib.HTTPConnection, 'getresponse')

        self.endpoint = 'http://example.com:8777'
        self.client = http.HTTPClient(self.endpoint, token=u'abc123')

    def tearDown(self):
        super(TestClient, self).tearDown()
        self.mock.UnsetStubs()

    def test_connection_refused(self):
        """
        Should receive a CommunicationError if connection refused.
        And the error should list the host and port that refused the
        connection
        """
        httplib.HTTPConnection.request(
            mox.IgnoreArg(),
            mox.IgnoreArg(),
            headers=mox.IgnoreArg(),
        ).AndRaise(socket.error())
        self.mock.ReplayAll()
        try:
            route = '/v1/meters'
            self.client.json_request('GET', route)
            self.fail('An exception should have bypassed this line.')
        except exc.CommunicationError, comm_err:
            fail_msg = ("Exception message '%s' should contain '%s'" %
                       (comm_err.message, route))
            self.assertThat(comm_err.message, Contains(route), fail_msg)

