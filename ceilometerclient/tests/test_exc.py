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


class ClientErrorTest(utils.BaseTestCase):
    exc_cls = exc.ClientError
    code = 'N/A'

    def setUp(self):
        super(ClientErrorTest, self).setUp()
        self.expected_base_str = "%s (HTTP %s)" % (self.exc_cls.__name__,
                                                   self.code)

    def test_str_no_details(self):
        exception = self.exc_cls()
        self.assertEqual(self.expected_base_str, str(exception))

    def test_str_no_json(self):
        exception = self.exc_cls(details="foo")
        self.assertEqual(self.expected_base_str, str(exception))

    def test_str_no_error_message(self):
        exception = self.exc_cls(details=json.dumps({}))
        self.assertEqual(self.expected_base_str, str(exception))

    def test_str_no_faultstring(self):
        exception = self.exc_cls(
            details=json.dumps({"error_message": {"foo": "bar"}}))
        self.assertEqual(self.expected_base_str, str(exception))

    def test_str_error_message_unknown_format(self):
        exception = self.exc_cls(
            details=json.dumps({"error_message": "oops"}))
        self.assertEqual(self.expected_base_str, str(exception))

    def test_str_faultstring(self):
        exception = self.exc_cls(
            details=json.dumps({"error_message": {"faultstring": "oops"}}))
        self.assertEqual(self.expected_base_str + " ERROR oops",
                         str(exception))


class HTTPBadRequestTest(ClientErrorTest):
    exc_cls = exc.HTTPBadRequest
    code = 400


class HTTPConflict(ClientErrorTest):
    exc_cls = exc.HTTPConflict
    code = 409
