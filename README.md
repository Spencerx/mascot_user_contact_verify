# Mascot Verification E-mail Reader

This software verifies, via LDAP, the users specified in a Mascot user XML
file, and provides a list of the valid e-mail addresses. Mascot is produced by
Matrix Science and is used in the analysis of Protein Mass Spectrometry data.

## Quick start

~~~~{.bash}
    $ python ./mascot-verified-email-list.py data/user.xml
    # presents a list of verified Mascot user e-mail addresses
~~~~

## Installation

To access the latest version of the software, you can access the git repository
on
[github.com]{http:://github.com/fls-bioinformatics-core/proteomics-mascot-user-contact-verify}.

~~~~{.bash}
    $ git clone git://github.com/fls-bioinformatics-core/proteomics-mascot-user-contact-verify
~~~~

The software depends on a custom library, also available from
[github.com](http://github.com/fls-bioinformatics-core/proteomics-python2.7-proteomics-lib).
However, if you used Git to obtain the software, you can use Git to download
the software:

~~~~{.bash}
	$ git submodules update --init
~~~~

## Description

This program was born out of a need to contact users of a local Mascot server
"on mass", but in an environment where some of the users with accounts had
moved on to greener pastures.

The software was designed to load in the Mascot user.xml file, identify the
users, and then query each user against the LDAP. Currently, an assumption is
made that the usernames used in the Mascot users are the same usernames used in
the LDAP verification: that is that the username is used as the key to verify
the Mascot users.

## Usage

The [Quick Start section](#quick-start) presents the best way of
running the software. The main exceptions to this, are if the
dependant library has been stored elsewhere. In that case, it is
necessary to inform Python where to look for the library (providing
that this is not on the Python library search path).

~~~~{.bash}
	$ PYTHONLIB=~/lib/python2.7/ ./log-time.py searches.log
~~~~

## Author(s) ##

Julian Selley <[j.selley@manchester.ac.uk](mailto:j.selley@manchester.ac.uk)>

## License ##

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but **WITHOUT ANY WARRANTY**; without even the implied warranty of
**MERCHANTABILITY** or **FITNESS FOR A PARTICULAR PURPOSE**.
