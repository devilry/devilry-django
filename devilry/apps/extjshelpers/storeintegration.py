from modelintegration import get_extjs_modelname, restfulcls_to_extjsmodel

def restfulcls_to_extjsstore(restfulcls, integrateModel=False, modelkwargs={},
                            pagesize=None):
    """
    Create an extjs store from the given restful class.

    :param restfulcls: A class defined using the :ref:`RESTful API <restful>`.
    :param integrateModel:
        Make the model a part of the store. Uses
        Uses :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjsmodel` with
        ``modelkwargs`` as arguments.
    :param modelkwargs: See ``integrateModel``.
    :param pagesize: An integer which is set as the pageSize parameter of the extjs store.
    """
    if integrateModel:
        model = restfulcls_to_extjsmodel(restfulcls, **modelkwargs)
    else:
        model = "'{modelname}'".format(modelname=get_extjs_modelname(restfulcls))
    if pagesize:
        jspagesize = ' pageSize: {0},'.format(pagesize)
    else:
        jspagesize = ''
    return """Ext.create('Ext.data.Store', {{
            model: {model},
            remoteFilter: true,
            remoteSort: true,{jspagesize}
            autoSync: true
        }})""".format(model=model, jspagesize=jspagesize)
