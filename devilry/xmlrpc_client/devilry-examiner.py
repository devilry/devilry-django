#!/usr/bin/env python

from cli import Cli, Login, Init
from examinercmd import ListAssignmentGroups, Sync, ListAssignments, \
        Feedback, InfoCmd


# TODO: make sure SESSION_COOKIE_SECURE is enabled by default or something
#       see: http://docs.djangoproject.com/en/dev/topics/http/sessions/#settings

extra_help = """To get started, initialize a devilry-checkout with these
steps:
    1. Create a new directory (we will call this the checkout-directory) and
       change to it.
        
        ~$ mkdir ~/devilrycheckout
        ~$ cd ~/devilrycheckout

    2. Initialize with the devilry-server:

        ~devilrycheckout/$ $prog init <server-url>

       Where server-url is the url to the root of the devilry-site you wish
       to initialize with. This might be something like
       "http://example.com/", or "http://example.com/devilry/". You can
       check if the url is correct by suffixing it with "/xmlrpc/" and open
       it in a browser. If the url takes you to the xmlrpc documentation,
       you have the correct url.

    3. Login using:

        ~devilrycheckout/$ $prog login

        If your username in the current shell session is not the same as your
        username with the devilry server, you must use:

        ~devilrycheckout/$ $prog login -u myuser

    4. Sync every delivery on every active assignment using:

        ~devilrycheckout/$ $prog sync

    5. See the help for 'sync', 'info' and 'feedback' for more information:

        ~devilrycheckout/$ $prog help sync
        ~devilrycheckout/$ $prog help info
        ~devilrycheckout/$ $prog help feedback

When you wish to update the local sync with new deliveries, or feedback
submitted by other examiners (if you work on assignments with more than one
examiner on each group), just repeat steps 3 and 4 within any directory
below the checout-directory. You might not have to login more than about
once a day, but this varies depending on how the devilry-server is
configured.
"""

if __name__ == '__main__':


    Cli([
        Init,
        Login,
        ListAssignments,
        ListAssignmentGroups,
        Sync,
        InfoCmd,
        Feedback], extra_help).cli()
