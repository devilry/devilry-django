from devilry.simplified import FieldSpec, FilterSpecs, FilterSpec



class RelatedUsersMetaBase:
    methods = ['create', 'read', 'update', 'delete', 'search']
    resultfields = FieldSpec('id', 'period', 'user', 'tags',
                             'user__username',
                             'user__devilryuserprofile__full_name',
                             'user__email')
    searchfields = FieldSpec('user__username', 'user__devilryuserprofile__full_name')
    editablefields = ('period', 'user')
    filters = FilterSpecs(FilterSpec('id', supported_comp=('exact',)),
                          FilterSpec('period', supported_comp=('exact',)),
                          FilterSpec('user', supported_comp=('exact',)))
