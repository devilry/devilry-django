from modelintegration import get_extjs_modelname, restfulcls_to_extjsmodel

def get_extjs_storeid(restfulcls, storeidsuffix=''):
    """
    Get the ExtJS store id for the given restful class.
    Generated from the store id and class name of
    ``restfulcls._meta.simplified``

    :param storeidsuffix: This string added to the end of the id.
    """
    simplified = restfulcls._meta.simplified
    prefix = get_extjs_modelname(restfulcls)
    return '{prefix}Store{storeidsuffix}'.format(prefix=prefix,
                                                 storeidsuffix=storeidsuffix)

def restfulcls_to_extjsstore(restfulcls, integrateModel=False, modelkwargs={},
                             storeidsuffix=''):
    """
    Create an extjs store from the given restful class.

    :param restfulcls: A class defined using the :ref:`RESTful API <restful>`.
    :param integrateModel:
        Make the model a part of the store. Uses
        Uses :func:`~devilry.apps.extjshelpers.modelintegration.restfulcls_to_extjsmodel` with
        ``modelkwargs`` as arguments.
    :param modelkwargs: See ``integrateModel``.
    :param storeidsuffix:
        Forwarded to func:`get_extjs_storeid` to generate the
        ``id`` of the store and to func:`devilry.extjshelpers.modelintegration.get_extjs_modelname`
        (as modelnamesuffix) to generate the model name.
    """
    if integrateModel:
        modelkwargs['modelnamesuffix'] = storeidsuffix
        model = restfulcls_to_extjsmodel(restfulcls, **modelkwargs)
    else:
        model = "'{modelname}'".format(modelname=get_extjs_modelname(restfulcls, storeidsuffix))


    return """Ext.create('Ext.data.Store', {{
            model: {model},
            id: '{id}',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        }})""".format(model=model, id=get_extjs_storeid(restfulcls, storeidsuffix))
