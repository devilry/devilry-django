Ext.define('devilry_extjsextras.EvenRandomSelection', {
    config: {
        /**
        * @cfg {Object[]} [selection]
        * The items in the selection pool.
        */
        selection: []
    },

    constructor: function(config) {
        this.pool = []; // Currently available subset of the selection. When this is empty, it is re-cloned from selection
        this.initConfig(config);
    },

    /** Get random item from the selection pool.
     *
     * The pool is filled with ``selection``, re-filled each time the pool is
     * empty. This method picks a random item from the pool. This means that
     * we always pick every item in the pool before we re-start picking items. */
    getRandomItem: function() {
        if(this.pool.length === 0) {
            this.pool = Ext.Array.clone(this.selection);
        }
        var randomIndex = Math.floor(Math.random() * (this.pool.length));
        var next = this.pool[randomIndex];
        Ext.Array.remove(this.pool, next);
        return next;
    }
});
