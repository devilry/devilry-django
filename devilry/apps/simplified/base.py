class SimplifiedBase(object):

    @classmethod
    def get_default_ordering(cls):
        return cls.CORE_MODEL._meta.ordering

    @classmethod
    def _set_orderby(cls, standard_opts):
        standard_opts['orderby'] = standard_opts.get('orderby',
                cls.get_default_ordering())

    #@classmethod
    #def update(cls, user, **kwargs):
        #obj = cls.get(user, id)
        #for attrname, value in kwargs.iteritems():
            #setattr(obj, attrname, value)
        #cls._set_parentnode_from_id(obj, parentnode_id)
        #obj.full_clean()
        #obj.save()
        #return obj

    #@classmethod
    #def _get(cls, fields, queryfields, qryset, standard_opts):
        #result = GetQryResult(fields, queryfields, qryset)
        #cls._set_orderby(standard_opts)
        #result._standard_operations(**standard_opts)
        #return result

    #@classmethod
    #def _save_model(cls, model):
        #""" Save and validate a model. """
        #model.full_clean()
        #model.save()
