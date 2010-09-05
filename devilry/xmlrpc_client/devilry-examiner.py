#!/usr/bin/env python

try:
    from devilry_xmlrpc_client.cli import (Cli, Login, Init, FormLogin)
    from devilry_xmlrpc_client.examinercmd import (ListAssignmentGroups,
            Sync, ListAssignments, Feedback, UnpublishFeedback,
            PublishFeedback, InfoCmd, Guide)
except ImportError:
    from devilry.xmlrpc_client.cli import (Cli, Login, Init, FormLogin)
    from devilry.xmlrpc_client.examinercmd import (ListAssignmentGroups,
            Sync, ListAssignments, Feedback, UnpublishFeedback,
            PublishFeedback, InfoCmd, Guide)


# TODO: make sure SESSION_COOKIE_SECURE is enabled by default or something
#       see: http://docs.djangoproject.com/en/dev/topics/http/sessions/#settings

if __name__ == '__main__':
    Cli([
        Guide,
        Init,
        Login,
        FormLogin,
        ListAssignments,
        ListAssignmentGroups,
        Sync,
        InfoCmd,
        Feedback,
        UnpublishFeedback,
        PublishFeedback]).cli()
