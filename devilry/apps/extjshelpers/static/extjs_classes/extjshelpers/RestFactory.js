Ext.define('devilry.extjshelpers.RestFactory', {
    requires: [
        'devilry.extjshelpers.Store',
        'devilry.extjshelpers.RestProxy'
    ],
    statics: {
        createProxy: function(role, name_lower) {
            return Ext.create('devilry.extjshelpers.RestProxy', {
                url: Ext.String.format('/{0}/restfulsimplified{1}/', role, name_lower)
            });
        },

        getModelName: function(role, name) {
            return Ext.String.format('devilry.{0}.models.{1}', role, name);
        },

        getModel: function(role, name) {
            return Ext.ModelManager.getModel(devilry.extjshelpers.RestFactory.getModelName(role, name));
        },

        createStore: function(role, name, config) {
            var args = {
                model: devilry.extjshelpers.RestFactory.getModelName(role, name)
            };
            Ext.apply(args, config);
            return Ext.create('devilry.extjshelpers.Store', args);
        }
    }
});
