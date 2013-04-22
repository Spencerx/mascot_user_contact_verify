#!/bin/env python
#
# -*- coding: utf-8 -*-
#
# Copyright (C) University of Manchester 2013 
#               Julian Selley <j.selley@manchester.ac.uk>
################################################################################

__docformat__ = 'restructuredtext en'

"""
Mascot Verified E-mail List Identifier
**************************************
This program identifies and produces a set of e-mail addresses from the Mascot
user.xml file. It checks against the LDAP server to make sure the users are
valid.

It depends on the 'proteomics' library, written by the same author. It also
depends on the ldap library.

    >>> $ PYTHONPATH=~/lib/python2.7/ ./mascot-verified-email-list.py \
    >>>                                 [-b LDAP_baseDN] \
    >>>                                 [-h LDAP_Host] \
    >>>                                 [-c Config_File] \ 
    >>>                                 [[-f] user.xml]

"""

# Metadata
__version__   = '0.01'
__author__    = 'Julian Selley <j.selley@manchester.ac.uk>'
__copyright__ = 'Copyright 2013 University of Manchester, Julian Selley <j.selley@manchester.ac.uk>'
__license__   = '''\
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
'''

# Imports
import ConfigParser
import ldap
import logging
import optparse
import os.path
import proteomics.mascot
import sys
import time

# Setup the logger
# parse command line options
cmdparser = optparse.OptionParser()
cmdparser.add_option('-b', '--base', action="store", type="string",
                     dest="ldap_base", default="o=anydomain.com",
                     help="the LDAP base DN to use")
cmdparser.add_option('-c', '--config', action="store", type="string",
                     dest="config", default="." + os.path.splitext(os.path.basename(__file__))[0] + "rc",
                     help="read config FILE", metavar="FILE")
cmdparser.add_option('-f', '--file', action="store", type="string",
                     dest="filename", default="user.xml",
                     help="read user FILE", metavar="FILE")
cmdparser.add_option('-H', '--host', action="store", type="string",
                     dest="ldap_host", default="127.0.0.1",
                     help="the LDAP host to use to verify")
(options, args) = cmdparser.parse_args()
if len(args) > 0:
    options.filename = args[0]

class VerifiedUserReader(tuple):
    """Verified User Reader.

    This class opens a Mascot User XML file, parses it and returns a list of the
    e-mail addresses. The class depends on the 'proteomics mascot' module.

    The code uses the logging module to generate debugging information.

    """
    def __new__(self, filename = os.path.join('data', 'user.xml'),
                proto = ldap.VERSION3, host = "127.0.0.1",
                base = "o=anydomain.com", search_scope = ldap.SCOPE_SUBTREE,
                retrieve_attr = None):
        """Constructor.

        Takes a filename (optional) detailing where the user file exists, in
        order to create the list of users. It then verifies each user via the
        username attribute against the LDAP (defaulting to a local
        implementation LDAP).

        @param  filename: the filename of the user XML to open (default: 'I{data/user.xml}')
        @type   filename: str

        """
        # obtain the users from the user file
        _user_f = proteomics.mascot.UserXMLInputFileReader(filename)
        _users = _user_f.read_file()

        # determined verified users by querying ldap
        self._verified_users = []
        # instantiate ldap connection
        logger.info("trying to initiate connection with LDAP server...")
        logger.debug("connecting to server {0}, using baseDN {1}".format(host, base))
        try:
            l = ldap.open(host)
            l.protocol_version = proto
        except ldap.LDAPERROR, e:
            logger.exception(e)
        logger.info("connection established successfully")

        # cycle through the users and query the ldap
        logger.info("starting to query LDAP about {0} users".format(len(_users)))
        for user in _users:
            logger.info("querying user {0} against LDAP".format(user))
            try:
                logger.debug("querying username: {0}".format(user.username))
                result_id = l.search(base, search_scope, "cn=" + user.username, retrieve_attr)
                while l:
                    result_type, result_data = l.result(result_id, 0)
                    logger.debug(result_type)
                    logger.debug("number of data: {0}".format(len(result_data)))
                    if (result_data == []):
                        logger.debug("no data obtained for user {0} from LDAP query".format(user))
                        break
                    else:
                        logger.debug("found user {0} in LDAP".format(user.username))
                        #logger.debug("LDAP search results: {0}".format(result_data))
                        if result_type == ldap.RES_SEARCH_ENTRY:
                            logger.info("adding user {0}".format(user.username))
                            self._verified_users.append(user)
            except ldap.LDAPError, e:
                logger.exception(e)

        return  tuple.__new__(self, self._verified_users)

if __name__ == '__main__':
    # setup logging
    logger = logging.getLogger(__name__)
    LOG_FORMAT = logging.Formatter('%(asctime)s %(name)-12s - %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(os.path.splitext(os.path.basename(__file__))[0] + ".log")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # use the formatter on both handlers
    fh.setFormatter(LOG_FORMAT)
    ch.setFormatter(LOG_FORMAT)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info("BEGIN")

    # read config file
    logger.info("trying to load config file (if it exists)...")
    logger.debug("checking if file {0} exists...".format(options.config))
    if os.path.isfile(options.config):
        logger.debug("config file exists; trying to open it...")
        try:
            config = ConfigParser.ConfigParser()
            logger.debug("attempting to read config file")
            config.read(options.config)
            logger.debug("... success! retrieving values...")
            options.ldap_host = config.get("ldap", "host")
            logger.debug("set ldap_host as {0}".format(ldap_host))
            options.ldap_base = config.get("ldap", "base")
            logger.debug("set ldap_base as {0}".format(ldap_base))
        except IOError, e:
            logger.exception(e)
        except ConfigParser.NoOptionError, e:
            logger.exception(e)

    # use VerifiedUserReader class to retreive and verify the users in the user.xml
    logger.info("retreiving and verifying users...")
    users = VerifiedUserReader(filename = options.filename, host = options.ldap_host,
                               base = options.ldap_base)
    for user in users:
        print("\"{0}\" <{1}>".format(user.fullname, user.email))

    logger.info("END")
