from ...restful import restful_modelapi, ModelRestfulView, RestfulManager
from simplified import SimplifiedNode, SimplifiedSubject, SimplifiedPeriod


__all__ = ('RestfulSimplifiedNode', 'RestfulSimplifiedSubject', 'RestfulSimplifiedPeriod')


administrator_restful = RestfulManager()

@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedNode(ModelRestfulView):
    class Meta:
        simplified = SimplifiedNode
        #foreignkey_fields = {'parentnode__id': RestfulSimplifiedNode}


@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedSubject(ModelRestfulView):
    class Meta:
        simplified = SimplifiedSubject
        as_foreignkey_fields = {'parentnode__id': RestfulSimplifiedNode}
        as_foreignkey_listconfig_tpl = '</span><span class="important">{long_name}</span><br/><span class="unimportant">{short_name}</span>'

@administrator_restful.register
@restful_modelapi
class RestfulSimplifiedPeriod(ModelRestfulView):
    class Meta:
        simplified = SimplifiedPeriod
        foreignkey_fields = {'parentnode__id': RestfulSimplifiedSubject}
        as_foreignkey_fieldgroups = ['subject']
        as_foreignkey_listconfig_tpl = '</span><span class="important">{long_name}</span><br/>'\
                '<span class="unimportant">{parentnode__short_name}.{short_name}</span>'
