'''
shift_out_in_between_dots.py

Copyright 2008 Jose Ramon Palanco 

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

from core.controllers.plugins.evasion_plugin import EvasionPlugin
from core.controllers.w3afException import w3afException
from core.data.url.HTTPRequest import HTTPRequest as HTTPRequest

# options
from core.data.options.option import option
from core.data.options.optionList import optionList


class shift_out_in_between_dots(EvasionPlugin):
    '''
    Insert between dots shift-in and shift-out control characters which are cancelled each other when they are below 
    @author: Jose Ramon Palanco( jose.palanco@hazent.com )
    '''

    def __init__(self):
        EvasionPlugin.__init__(self)

    def modifyRequest(self, request ):
        '''
        Mangles the request
        
        @parameter request: HTTPRequest instance that is going to be modified by the evasion plugin
        @return: The modified request

        >>> from core.data.parsers.urlParser import url_object
        >>> import re
        >>> sosibd = shift_out_in_between_dots()

        >>> u = url_object('http://www.w3af.com/')
        >>> r = HTTPRequest( u )
        >>> sosibd.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/'
        
        >>> u = url_object('http://www.w3af.com/../')
        >>> r = HTTPRequest( u )
        >>> sosibd.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/.%0E%0F./'

        >>> u = url_object('http://www.w3af.com/abc/def/.././jkl.htm')
        >>> r = HTTPRequest( u )
        >>> sosibd.modifyRequest( r ).url_object.url_string
        u'http://www.w3af.com/abc/def/.%0E%0F././jkl.htm'
        >>> #
        >>> #    The plugins should not modify the original request
        >>> #
        >>> u.url_string
        u'http://www.w3af.com/abc/def/.././jkl.htm'

        '''
        # We mangle the URL
        path = request.url_object.getPath()
        path = path.replace('/../','/.%0E%0F./' )
        
        # Finally, we set all the mutants to the request in order to return it
        new_url = request.url_object.copy()
        new_url.setPath( path )
        new_req = HTTPRequest( new_url , request.get_data(), 
                               request.headers, request.get_origin_req_host() )
        
        return new_req

    def get_options( self ):
        '''
        @return: A list of option objects for this plugin.
        '''    
        ol = optionList()
        return ol

    def set_options( self, OptionList ):
        '''
        This method sets all the options that are configured using the user interface 
        generated by the framework using the result of get_options().
        
        @parameter OptionList: A dictionary with the options for the plugin.
        @return: No value is returned.
        ''' 
        pass
        
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be run before the
        current one.
        '''        
        return []

    def getPriority( self ):
        '''
        This function is called when sorting evasion plugins.
        Each evasion plugin should implement this.
        
        @return: An integer specifying the priority. 100 is run first, 0 last.
        '''
        return 20
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return r'''
        This evasion plugin insert between dots shift-in and shift-out control 
        characters which are cancelled each other when they are below so some 
        ".." filters are bypassed        
 
        Example:
            Input:      '../../../../../../../../etc/passwd'
            Output:     '.%0E%0F./.%0E%0F./.%0E%0F./.%0E%0F./.%0E%0F./.%0E%0F./.%0E%0F./.%0E%0F./etc/passwd'
        '''
