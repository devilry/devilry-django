Ext.define('devilry.extjshelpers.EvenRandomSelection', {
    config: {
        selection: []
    },

    constructor: function(config) {
        this.pool = []; // Currently available subset of the selection. When this is empty, it is re-cloned from selection
        this.initConfig(config);
        this.callParent([config]);
    },

    getRandomItem: function() {
        if(this.pool.length === 0) {
            this.pool = Ext.Array.clone(this.selection);
        }
        var randomIndex = Math.floor(Math.random() * (this.pool.length));
        var next = this.pool[randomIndex];
        Ext.Array.remove(this.pool, next);
        return next;
    },
});
