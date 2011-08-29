Ext.define('devilry.extjshelpers.DateTime', {
    statics: {
        restfulNow: function() {
            return devilry.extjshelpers.DateTime.restfulFormat(new Date(Ext.Date.now()));
        },

        restfulFormat: function(dateobj) {
            return Ext.Date.format(dateobj, Ext.Date.patterns.RestfulDateTime);
        }
    }
});
