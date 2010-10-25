from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.db.models import Q

from devilry.ui.messages import UiMessages
from devilry.ui.filtertable import FilterTable, Action, Filter


admins_help_text = _('Comma-separated list of administrators. Just start '\
        'typing a username, and you will get a dropdown of matching names. ' \
        'Administrator rights are inherited from the ' \
        'parentnode, and any parentnode higher up in the hierarchy. ' \
        'Administrators have full access, so you should be careful ' \
        'about who you give this '
        'privilege.')


def iter_filtertable_selected(postdata, clsname):
    prefix = 'autocomplete-%s-cb' % clsname
    for key, value in postdata.iteritems():
        if key.startswith(prefix):
            yield key, value


class FilterHasAdmins(Filter):
    def __init__(self):
        super(FilterHasAdmins, self).__init__(_("Has administrators?"))

    def get_labels(self, properties):
        return [_("All"), _("Yes"), _("No")]

    def filter(self, properties, dataset, selected):
        choice = selected[0]
        if choice == 1:
            dataset = dataset.filter(admins__isnull=False)
        elif choice == 2:
            dataset = dataset.filter(admins__isnull=True)
        return dataset


class NodeAction(Action):
    def get_url(self, properties):
        return reverse(self.url)

class BaseNodeFilterTable(FilterTable):
    nodecls = None
    search_help = _('Search for any part of the "short name", "long name" '\
            'or the username of administrators.')
    default_order_by = "short_name"
    default_order_asc = True
    use_rowactions = True
    filters = [FilterHasAdmins()]

    @classmethod
    def get_selected_nodes(cls, request):
        nodes = []
        for node_id in cls.get_selected_ids(request):
            node = get_object_or_404(cls.nodecls, id=node_id)
            if node.can_save(request.user):
                nodes.append(node)
        return nodes

    def __init__(self, request):
        super(BaseNodeFilterTable, self).__init__(request)
        self.set_properties(nodecls=self.nodecls)

    def create_dataset(self):
        dataset = self.nodecls.where_is_admin_or_superadmin(self.request.user)
        total = dataset.count()
        return total, dataset

    def search(self, dataset, qry):
        return dataset.filter(
                Q(short_name__contains=qry) |
                Q(long_name__contains=qry) |
                Q(admins__username__contains=qry))


def deletemany_generic(request, nodecls, filtertblcls, successurl=None):
    successurl = successurl or reverse('devilry-main')
    clsname = nodecls.__name__.lower()
    prefix = 'autocomplete-%s-cb' % clsname
    if request.method == 'POST':
        nodes = []
        nodes = filtertblcls.get_selected_nodes(request)
        nodestr = []
        for node in nodes:
            nodestr.append(str(node))
        for node in nodes:
            node.delete()
        messages = UiMessages()
        messages.add_success(_("Successfully deleted: %(nodes)s" % dict(
            nodes = ', '.join(nodestr))))
        messages.save(request)
        return HttpResponseRedirect(successurl)


class EditBase(object):
    VIEW_NAME = None
    MODEL_CLASS = None

    def __init__(self, request, obj_id):
        self.request = request
        self.messages = UiMessages()
        self.messages.load(request)
        self.parent_model = self.MODEL_CLASS.parentnode.field.related.parent_model
        model_name = self.MODEL_CLASS._meta.verbose_name
        self.model_name_dict = {'model_name': model_name}
        self.forbidden = False

        if obj_id == None:
            self.is_new = True
            self.obj = self.MODEL_CLASS()
            self.post_url = reverse('devilry-admin-create_%s' % self.VIEW_NAME)
        else:
            self.is_new = False
            self.obj = get_object_or_404(self.MODEL_CLASS, pk=obj_id)
            if not self.obj.can_save(self.request.user):
                self.forbidden = True
                return
            self.post_url = reverse(
                    'devilry-admin-edit_%s' % self.VIEW_NAME,
                    args = [str(self.obj.pk)])

    def create_form(self):
        raise NotImplementedError()

    def get_parent_url(self):
        raise NotImplementedError()
    
    #def get_reverse_url(self, *args):
        #return reverse('devilry.addons.admin.views.edit_' + self.VIEW_NAME,
                #args=args)

    def create_view(self):
        if self.forbidden:
            return HttpResponseForbidden("Forbidden")

        form_cls = self.create_form()

        if self.request.POST:
            objform = form_cls(self.request.POST, instance=self.obj)
            if objform.is_valid():
                if not self.obj.can_save(self.request.user):
                    return HttpResponseForbidden("Forbidden")
                objform.save()
                messages = UiMessages()
                messages.add_success(_("%(model_name)s successfully saved." % 
                    self.model_name_dict))
                messages.save(self.request)
                success_url = reverse(
                        'devilry-admin-edit_%s' % self.VIEW_NAME,
                        args = [str(self.obj.pk)])
                return HttpResponseRedirect(success_url)
        else:
            objform = form_cls(instance=self.obj)

        if self.obj.id == None:
            self.title = _('Create %(model_name)s') % self.model_name_dict
        else:
            self.title = _('Edit %(model_name)s' % self.model_name_dict)

        parent_url_label = self.MODEL_CLASS._meta.verbose_name_plural
        parent_url = self.get_parent_url()
        return render_to_response('devilry/admin/edit_node.django.html', {
            'title': self.title,
            'model_plural_name': self.MODEL_CLASS._meta.verbose_name_plural,
            'nodeform': objform,
            'messages': self.messages,
            'post_url': self.post_url,
            'parent_url_label': parent_url_label,
            'parent_url': parent_url,
            }, context_instance=RequestContext(self.request))
