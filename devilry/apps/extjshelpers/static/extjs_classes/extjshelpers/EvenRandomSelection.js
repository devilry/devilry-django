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
            console.log('hei');
            this.pool = Ext.Array.clone(this.selection);
        }
        console.log(this.pool.length, this.pool, this.selection);
        var randomIndex = Math.floor(Math.random() * (this.pool.length));
        var next = this.pool[randomIndex];
        console.log(next);
        Ext.Array.remove(this.pool, next);
        return next;
    },
});
