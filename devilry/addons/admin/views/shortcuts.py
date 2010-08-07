from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.translation import ugettext as _

from devilry.ui.messages import UiMessages


def iter_filtertable_selected(postdata, clsname):
    prefix = 'autocomplete-%s-cb' % clsname
    for key, value in postdata.iteritems():
        if key.startswith(prefix):
            yield key, value


def deletemany_generic(request, nodecls, successurl=None):
    successurl = successurl or reverse('main')
    clsname = nodecls.__name__.lower()
    prefix = 'autocomplete-%s-cb' % clsname
    if request.method == 'POST':
        nodes = []
        for key, value in iter_filtertable_selected(request.POST, clsname):
            node = nodecls.objects.get(id=value)
            if node.can_save(request.user):
                nodes.append(node)
            else:
                raise ValueError(
                        "No permission to delete %(node)s" % node)
        for node in nodes:
            node.delete()
        return HttpResponseRedirect(successurl)


class EditBase(object):
    VIEW_NAME = None
    MODEL_CLASS = None

    def __init__(self, request, obj_id, successful_save):
        self.request = request
        self.messages = UiMessages()
        self.parent_model = self.MODEL_CLASS.parentnode.field.related.parent_model
        model_name = self.MODEL_CLASS._meta.verbose_name
        self.model_name_dict = {'model_name': model_name}

        if successful_save:
            self.messages.add_success(_("%(model_name)s successfully saved." % 
                self.model_name_dict))

        if obj_id == None:
            self.is_new = True
            self.obj = self.MODEL_CLASS()
            self.post_url = reverse('devilry-admin-create_%s' % self.VIEW_NAME)
        else:
            self.is_new = False
            self.obj = get_object_or_404(self.MODEL_CLASS, pk=obj_id)
            if not self.obj.can_save(self.request.user):
                return HttpResponseForbidden("Forbidden")
            self.post_url = reverse(
                    'devilry-admin-edit_%s' % self.VIEW_NAME,
                    args = [str(self.obj.pk)])

    def create_form(self):
        raise NotImplementedError, "create_form must be implemented"
    
    def get_reverse_url(self, *args):
        return reverse('devilry.addons.admin.views.edit_' + self.VIEW_NAME, args=args)

    def create_view(self):
        form_cls = self.create_form()

        if self.request.POST:
            objform = form_cls(self.request.POST, instance=self.obj)
            if objform.is_valid():
                if not self.obj.can_save(self.request.user):
                    return HttpResponseForbidden("Forbidden")
                objform.save()
                success_url = reverse(
                        'devilry-admin-edit_%s-success' % self.VIEW_NAME,
                        args = [str(self.obj.pk)])
                return HttpResponseRedirect(success_url)
        else:
            objform = form_cls(instance=self.obj)

        if self.obj.id == None:
            self.title = _('Create %(model_name)s') % self.model_name_dict
        else:
            self.title = _('Edit %(model_name)s' % self.model_name_dict)

        return render_to_response('devilry/admin/edit_node.django.html', {
            'title': self.title,
            'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': objform,
            'messages': self.messages,
            'post_url': self.post_url,
            }, context_instance=RequestContext(self.request))
