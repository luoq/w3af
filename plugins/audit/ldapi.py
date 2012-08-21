'''
ldapi.py

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
from __future__ import with_statement

import core.data.kb.knowledgeBase as kb
import core.data.kb.vuln as vuln
import core.data.constants.severity as severity
import core.controllers.outputManager as om

from core.controllers.plugins.audit_plugin import AuditPlugin
from core.data.esmre.multi_in import multi_in
from core.data.fuzzer.fuzzer import createMutants


class ldapi(AuditPlugin):
    '''
    Find LDAP injection bugs.
    @author: Andres Riancho ( andres.riancho@gmail.com )
    '''

    LDAP_ERRORS = (
        # Not sure which lang or LDAP engine
        'supplied argument is not a valid ldap',
    
        # Java
        'javax.naming.NameNotFoundException',
        'LDAPException',
        'com.sun.jndi.ldap',
        
        # PHP
        'Search: Bad search filter',
        
        # http://support.microsoft.com/kb/218185
        'Protocol error occurred',
        'Size limit has exceeded',
        'An inappropriate matching occurred',
        'A constraint violation occurred',
        'The syntax is invalid',
        'Object does not exist',
        'The alias is invalid',
        'The distinguished name has an invalid syntax',
        'The server does not handle directory requests',
        'There was a naming violation',
        'There was an object class violation',
        'Results returned are too large',
        'Unknown error occurred',
        'Local error occurred',
        'The search filter is incorrect',
        'The search filter is invalid',
        'The search filter cannot be recognized',
        
        # OpenLDAP
        'Invalid DN syntax',
        'No Such Object',

        # IPWorks LDAP
        # http://www.tisc-insight.com/newsletters/58.html
        'IPWorksASP.LDAP',

        # https://entrack.enfoldsystems.com/browse/SERVERPUB-350
        'Module Products.LDAPMultiPlugins'
    )
            
    _multi_in = multi_in( LDAP_ERRORS )

    def __init__(self):
        AuditPlugin.__init__(self)
        
        # Internal variables
        self._errors = []
        
    def audit(self, freq ):
        '''
        Tests an URL for LDAP injection vulnerabilities.
        
        @param freq: A fuzzable_request
        '''
        oResponse = self._uri_opener.send_mutant(freq)
        ldapiStrings = self._get_ldapi_strings()
        mutants = createMutants( freq , ldapiStrings, oResponse=oResponse )
        
        self._send_mutants_in_threads(self._uri_opener.send_mutant,
                                 mutants,
                                 self._analyze_result)
            
    def _get_ldapi_strings( self ):
        '''
        Gets a list of strings to test against the web app.
        
        @return: A list with all ldapi strings to test.
        '''
        ldap_strings = []
        ldap_strings.append("^(#$!@#$)(()))******")
        return ldap_strings

    def _analyze_result( self, mutant, response ):
        '''
        Analyze results of the _send_mutant method.
        '''
        #
        #   I will only report the vulnerability once.
        #
        if self._has_no_bug(mutant):
            
            ldap_error_list = self._find_ldap_error( response )
            for ldap_error_string in ldap_error_list:
                if ldap_error_string not in mutant.getOriginalResponseBody():
                    v = vuln.vuln( mutant )
                    v.setPluginName(self.getName())
                    v.setId( response.id )
                    v.setSeverity(severity.HIGH)
                    v.setName( 'LDAP injection vulnerability' )
                    v.setDesc( 'LDAP injection was found at: ' + mutant.foundAt() )
                    v.addToHighlight( ldap_error_string )
                    kb.kb.append( self, 'ldapi', v )
                    break
    
    def end(self):
        '''
        This method is called when the plugin wont be used anymore.
        '''
        self.print_uniq( kb.kb.getData( 'ldapi', 'ldapi' ), 'VAR' )
        
    def _find_ldap_error( self, response ):
        '''
        This method searches for LDAP errors in html's.
        
        @parameter response: The HTTP response object
        @return: A list of errors found on the page
        '''
        res = []
        for match_string in self._multi_in.query( response.body ):
            msg = 'Found LDAP error string. '
            msg += 'The error returned by the web application is (only a fragment is shown): "'
            msg += match_string + '". The error was found on '
            msg += 'response with id ' + str(response.id) + '.'
            om.out.information(msg)
            res.append( match_string )
        return res
        
    def getPluginDeps( self ):
        '''
        @return: A list with the names of the plugins that should be run before the
        current one.
        '''
        return ['grep.error_500']
    
    def getLongDesc( self ):
        '''
        @return: A DETAILED description of the plugin functions and features.
        '''
        return '''
        This plugin will find LDAP injections by sending a specially crafted string to every
        parameter and analyzing the response for LDAP errors.
        '''
