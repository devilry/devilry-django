from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.translation import ugettext as _

from devilry.ui.messages import UiMessages



def list_nodes_generic(request, nodecls):
    return render_to_response('devilry/admin/list_nodes.django.html', {
        'model_plural_name': nodecls._meta.verbose_name_plural,
        'nodes': nodecls.where_is_admin(request.user),
        }, context_instance=RequestContext(request))


def delete_generic(request, nodecls, id, message=""):
    node = get_object_or_404(nodecls, id=id)
    clsname = nodecls.__name__.lower()
    deleteurl = reverse('devilry-admin-delete_%s' % clsname,
            args=[id])
    cancelurl = reverse('devilry-admin-edit_%s' % clsname,
            args=[id])
    if "confirm" in request.GET:
        node.delete()
        successurl = reverse('main')
        return HttpResponseRedirect(successurl)
    return render_to_response('devilry/admin/confirm_delete.django.html', {
        'deleteurl': deleteurl,
        'cancelurl': cancelurl,
        'message': message,
        'what_to_delete': node,
        }, context_instance=RequestContext(request))


def deletemany_generic(request, nodecls):
    prefix = 'autocomplete-%s-cb' % nodecls.__name__.lower()
    if request.method == 'POST':
        nodes = []
        for key, value in request.POST.iteritems():
            if key.startswith(prefix):
                node = nodecls.objects.get(id=value)
                if node.can_save(request.user):
                    nodes.append(node)
                else:
                    raise ValueError(
                            "No permission to delete %(node)s" % node)
        for node in nodes:
            node.delete()
        successurl = reverse('main')
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
