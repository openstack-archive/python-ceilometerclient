# Copyright 2012 OpenStack LLC.
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

import unittest
from ceilometerclient.common import http
from tests import utils


fixtures = {}


class HttpClientTest(unittest.TestCase):

    def setUp(self):
        self.api = utils.FakeAPI(fixtures)

    def test_url_generation_with_connection_params(self):
        result = self.api.url_generation('GET', '/v1/meters', 'test_connection_params')
        self.assertEqual(result, 'test_connection_params/v1/meters')

    def test_url_generation_without_connection_params(self):
        result = self.api.url_generation('GET', '/v1/meters')
        self.assertEqual(result, '/v1/meters')
