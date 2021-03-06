'''
test_errors.py

Copyright 2013 Andres Riancho

This file is part of w3af, http://w3af.org/ .

w3af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w3af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w3af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

'''
import unittest
import urllib2

from nose.plugins.attrib import attr

from core.controllers.misc.number_generator import consecutive_number_generator

from core.data.parsers.url import URL
from core.data.constants.response_codes import NOT_FOUND
from core.data.url.HTTPRequest import HTTPRequest
from core.data.url import opener_settings


class TestErrorHandler(unittest.TestCase):
    
    def setUp(self):
        consecutive_number_generator.reset()
    
    @attr('moth')
    def test_error_handler_id(self):
        '''Verify that the blacklist handler works as expected'''
        fail_url = URL('http://moth/abc/def/do-not-exist.foo')
        
        settings = opener_settings.OpenerSettings()
        settings.build_openers()
        opener = settings.get_custom_opener()

        request = HTTPRequest(fail_url)
        try:
            opener.open(request)
        except urllib2.HTTPError, response:
            self.assertEqual(response.code, NOT_FOUND)
            self.assertEqual(response.id, 1)
