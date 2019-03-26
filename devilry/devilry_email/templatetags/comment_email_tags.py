from django import template

from cradmin_legacy.crinstance import reverse_cradmin_url

register = template.Library()


@register.simple_tag
def groupcomment_email_commentfile_absolute_url(commentfile, domain_scheme, crinstance_id):
    """
    Get the absolute url to download a commentfile.
    """
    group = commentfile.comment.feedback_set.group
    domain_scheme = domain_scheme.rstrip('/')
    return '{}{}'.format(
        domain_scheme,
        reverse_cradmin_url(
            instanceid=crinstance_id,
            appname='download',
            viewname='file-download',
            roleid=group.id,
            kwargs={
                'commentfile_id': commentfile.id
            }
        ))