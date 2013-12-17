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

from ceilometerclient.tests import utils


class HTTPBadRequestTest(utils.BaseTestCase):

    def test_str_no_details(self):
        exception = exc.HTTPBadRequest()
        self.assertEqual("HTTPBadRequest (HTTP 400)", str(exception))

    def test_str_no_json(self):
        exception = exc.HTTPBadRequest(details="foo")
        self.assertEqual("HTTPBadRequest (HTTP 400)", str(exception))

    def test_str_no_error_message(self):
        exception = exc.HTTPBadRequest(details=json.dumps({}))
        self.assertEqual("HTTPBadRequest (HTTP 400)", str(exception))

    def test_str_no_faultstring(self):
        exception = exc.HTTPBadRequest(
            details=json.dumps({"error_message": {"foo": "bar"}}))
        self.assertEqual("HTTPBadRequest (HTTP 400)", str(exception))

    def test_str_error_message_unknown_format(self):
        exception = exc.HTTPBadRequest(
            details=json.dumps({"error_message": "oops"}))
        self.assertEqual("HTTPBadRequest (HTTP 400)", str(exception))

    def test_str_faultstring(self):
        exception = exc.HTTPBadRequest(
            details=json.dumps({"error_message": {"faultstring": "oops"}}))
        self.assertEqual("HTTPBadRequest (HTTP 400) ERROR oops",
                         str(exception))
