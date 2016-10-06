# Copyright 2013 eNovance
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

import json

from ceilometerclient import exc
from ceilometerclient.tests.unit import utils

HTTPEXCEPTIONS = {'HTTPBadRequest': exc.HTTPBadRequest,
                  'HTTPUnauthorized': exc.HTTPUnauthorized,
                  'HTTPForbidden': exc.HTTPForbidden,
                  'HTTPNotFound': exc.HTTPNotFound,
                  'HTTPMethodNotAllowed': exc.HTTPMethodNotAllowed,
                  'HTTPConflict': exc.HTTPConflict,
                  'HTTPOverLimit': exc.HTTPOverLimit,
                  'HTTPInternalServerError': exc.HTTPInternalServerError,
                  'HTTPNotImplemented': exc.HTTPNotImplemented,
                  'HTTPBadGateway': exc.HTTPBadGateway,
                  'HTTPServiceUnavailable': exc.HTTPServiceUnavailable}


class HTTPExceptionsTest(utils.BaseTestCase):
    def test_str_no_details(self):
        for k, v in HTTPEXCEPTIONS.items():
            exception = v()
            ret_str = k + " (HTTP " + str(exception.code) + ")"
            self.assertEqual(ret_str, str(exception))

    def test_str_no_json(self):
        for k, v in HTTPEXCEPTIONS.items():
            exception = v(details="foo")
            ret_str = k + " (HTTP " + str(exception.code) + ") foo"
            self.assertEqual(ret_str, str(exception))

    def test_str_no_error_message(self):
        for k, v in HTTPEXCEPTIONS.items():
            exception = v(details=json.dumps({}))
            ret_str = k + " (HTTP " + str(exception.code) + ")"
            self.assertEqual(ret_str, str(exception))

    def test_str_no_faultstring(self):
        for k, v in HTTPEXCEPTIONS.items():
            exception = v(
                details=json.dumps({"error_message": {"foo": "bar"}}))
            ret_str = (k + " (HTTP " + str(exception.code) + ") " +
                       str({u'foo': u'bar'}))
            self.assertEqual(ret_str, str(exception))

    def test_str_error_message_unknown_format(self):
        for k, v in HTTPEXCEPTIONS.items():
            exception = v(details=json.dumps({"error_message": "oops"}))
            ret_str = k + " (HTTP " + str(exception.code) + ") oops"
            self.assertEqual(ret_str, str(exception))

    def test_str_faultstring(self):
        for k, v in HTTPEXCEPTIONS.items():
            exception = v(details=json.dumps(
                {"error_message": {"faultstring": "oops"}}))
            ret_str = k + " (HTTP " + str(exception.code) + ") ERROR oops"
            self.assertEqual(ret_str, str(exception))

    def test_from_response(self):
        class HTTPLibLikeResponse(object):
            status = 400

        class RequestsLikeResponse(object):
            status_code = 401

        class UnexpectedResponse(object):
            code = 200

        self.assertEqual(HTTPLibLikeResponse.status,
                         exc.from_response(HTTPLibLikeResponse).code)
        self.assertEqual(RequestsLikeResponse.status_code,
                         exc.from_response(RequestsLikeResponse).code)
        self.assertRaises(TypeError, exc.from_response, UnexpectedResponse)
