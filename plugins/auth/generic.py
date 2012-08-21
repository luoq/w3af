'''
generic.py

Copyright 2011 Andres Riancho

This file is part of w3af, w3af.sourceforge.net .

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
from urllib import urlencode

from core.data.options.option import option
from core.data.options.optionList import optionList
from core.controllers.plugins.auth_plugin import AuthPlugin
from core.controllers.w3afException import w3afException
import core.controllers.outputManager as om


class generic(AuthPlugin):
    '''Generic authentication plugin.'''

    def __init__(self):
        AuthPlugin.__init__(self)
        self.username = ''
        self.password = ''
        self.username_field = ''
        self.password_field = ''
        self.auth_url = ''
        self.check_url = ''
        self.check_string = ''
        self._login_error = True
        
    def login(self):
        '''
        Login to the application.
        '''

        msg = 'Logging into the application using %s/%s' % (self.username, self.password)
        om.out.debug( msg )

        try:
            # TODO Why we don't use httpPostDataRequest here?
            self._uri_opener.POST(self.auth_url, urlencode({
                self.username_field: self.username,
                self.password_field: self.password,
            }))
            if not self.is_logged():
                raise Exception("Can't login into web application as %s/%s" 
                                % (self.username, self.password))
            else:
                om.out.debug( 'Login success for %s/%s' % (self.username, self.password) )
                return True
        except Exception, e:
            if self._login_error:
                om.out.error(str(e))
                self._login_error = False
            return False

    def logout(self):
        '''User login.'''
        return None

    def is_logged(self):
        '''Check user session.'''
        try:
            body = self._uri_opener.GET(self.check_url, grep=False).body
            logged_in = self.check_string in body

            msg_yes = 'User "%s" is currently logged into the application'
            msg_no = 'User "%s" is NOT logged into the application'
            msg = msg_yes if logged_in else msg_no
            om.out.debug( msg % self.username )

            return logged_in
        except Exception:
            return False
   
    def get_options(self):
        '''
        @return: A list of option objects for this plugin.
        '''
        options = [ 
                ('username', self.username, 'string', 'Username for using in the authentication'),
                ('password', self.password, 'string', 'Password for using in the authentication'),
                ('username_field', self.username_field, 'string', 'Username HTML field name'),
                ('password_field', self.password_field, 'string', 'Password HTML field name'),
                ('auth_url', self.auth_url, 'url', 
                    'Auth URL - URL for POSTing the authentication information'),
                ('check_url', self.check_url, 'url', 
                    'Check session URL - URL in which response body check_string will be searched'),
                ('check_string', self.check_string, 'string', 
                    'String for searching on check_url page to determine if user\
                    is logged in the web application'),
                ]
        ol = optionList()
        for o in options:
            ol.add(option(o[0], o[1], o[3], o[2]))
        return ol

    def set_options(self, optionsMap):
        '''
        This method sets all the options that are configured using 
        the user interface generated by the framework using 
        the result of get_options().
        
        @parameter optionsMap: A dict with the options for the plugin.
        @return: No value is returned.
        ''' 
        self.username = optionsMap['username'].getValue()
        self.password = optionsMap['password'].getValue()
        self.username_field = optionsMap['username_field'].getValue()
        self.password_field = optionsMap['password_field'].getValue()
        self.check_string = optionsMap['check_string'].getValue()
        self.auth_url = optionsMap['auth_url'].getValue()
        self.check_url = optionsMap['check_url'].getValue()

        for o in optionsMap:
            if not o.getValue():
                raise w3afException(
                        "All parameters are required and can't be empty."
                        )

    def getPluginDeps(self):
        '''
        @return: A list with the names of the plugins that should be run 
        before the current one.
        '''
        return []

    def getLongDesc(self):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This authentication plugin can login to web application with generic
        authentication schema.
        
        Three configurable parameters exist:
            - username
            - password
            - username_field
            - password_field
            - auth_url
            - check_url
            - check_string
        '''


