'''
oracle_discovery.py

Copyright 2006 Andres Riancho

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
import core.controllers.outputManager as om

# options
from core.data.options.option import option
from core.data.options.optionList import optionList

from core.controllers.plugins.crawl_plugin import CrawlPlugin
from core.controllers.w3afException import w3afRunOnce

import core.data.kb.knowledgeBase as kb
from core.controllers.core_helpers.fingerprint_404 import is_404
import core.data.kb.info as info

import re


class oracle_discovery(CrawlPlugin):
    '''
    Find Oracle applications on the remote web server.
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''

    def __init__(self):
        CrawlPlugin.__init__(self)
        self._exec = True

    def crawl(self, fuzzable_request ):
        '''
        GET some files and parse them.
        
        @parameter fuzzable_request: A fuzzable_request instance that contains
                                    (among other things) the URL to test.
        '''
        if not self._exec :
            # This will remove the plugin from the crawl plugins to be run.
            raise w3afRunOnce()
            
        else:
            # Only run once
            self._exec = False
            
            base_url = fuzzable_request.getURL().baseUrl()
            
            for url, regex_string in self.getOracleData():

                oracle_discovery_URL = base_url.urlJoin( url )
                response = self._uri_opener.GET( oracle_discovery_URL, cache=True )
                
                if not is_404( response ):
                    for fr in self._create_fuzzable_requests( response ):
                        self.output_queue.put(fr)
                    if re.match( regex_string , response.getBody(), re.DOTALL):
                        i = info.info()
                        i.setPluginName(self.getName())
                        i.setName('Oracle application')
                        i.setURL( response.getURL() )
                        i.setDesc( self._parse( url, response ) )
                        i.setId( response.id )
                        kb.kb.append( self, 'info', i )
                        om.out.information( i.getDesc() )
                    else:
                        msg = 'oracle_discovery found the URL: ' + response.getURL()
                        msg += ' but failed to parse it. The content of the URL is: "'
                        msg += response.getBody() + '".'
                        om.out.debug( msg )
    
    def _parse( self, url, response ):
        '''
        This function parses responses and returns the message to be setted in the
        information object.

        @parameter url: The requested url
        @parameter response: The response object
        @return: A string with the message
        '''
        res = ''
        if url == '/portal/page':
            # Check if I can get the oracle version
            # <html><head><title>PPE is working</title></head><body>
            # PPE version 1.3.4 is working.</body></html>
            regex_str = '<html><head><title>PPE is working</title></head><body>PPE version'
            regex_str += ' (.*?) is working\.</body></html>'
            if re.match( regex_str, response.getBody() ):
            
                version = re.findall( regex_str, response.getBody() )[0]
                res = 'Oracle Parallel Page Engine version "'+ version
                res += '" was detected at: "' + response.getURL() + '".'
            
            else:
                # I dont have the version!
                res = 'Oracle Parallel Page Engine was detected at: ' +  response.getURL()
                
        elif url == '/reports/rwservlet/showenv':
            # Example string: Reports Servlet Omgevingsvariabelen 9.0.4.2.0
            try:
                version = re.findall( 'Reports Servlet .*? (.*)' , response.getBody() )[0][:-1]
                res = 'Oracle reports version "'+version+'" was detected at: ' + response.getURL()
            except:
                msg = 'Failed to parse the Oracle reports version from HTML: ' + response.getBody()
                om.out.error( msg )
                res = 'Oracle reports was detected at: ' + response.getURL()
                
        return res
    
    def getOracleData( self ):
        '''
        @return: A list of tuples with ( url, regex_string )
        '''
        res = []

        regex_string = '<html><head><title>PPE is working</title></head><body>'
        regex_string += 'PPE .*?is working\.</body></html>'
        res.append( ('/portal/page', regex_string) )

        regex_string = '.*<title>Oracle Application Server Reports Services - Servlet</title>.*'
        res.append( ('/reports/rwservlet/showenv', regex_string) )
        return res
    
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
        return ['grep.path_disclosure']
        
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin fetches some Oracle Application Server URLs and parses the information
        available on them.
        '''
