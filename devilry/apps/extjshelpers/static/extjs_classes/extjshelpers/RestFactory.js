Ext.define('devilry.extjshelpers.RestFactory', {
    requires: [
        'devilry.extjshelpers.models.Delivery',
        'devilry.extjshelpers.models.Deadline',
        'devilry.extjshelpers.Store',
        'devilry.extjshelpers.RestProxy'
    ],
    statics: {
        createProxy: function(role, name_lower) {
            return Ext.create('devilry.extjshelpers.RestProxy', {
                url: Ext.String.format('/{0}/restfulsimplified{1}/', role, name_lower)
            });
        },

        createStore: function(role, name) {
            return Ext.create('devilry.extjshelpers.Store', {
                model: 'devilry.extjshelpers.models.' + name,
                //proxy: devilry.extjshelpers.RestFactory.createProxy(role, name.toLowerCase())
            });
        }
    }
});
