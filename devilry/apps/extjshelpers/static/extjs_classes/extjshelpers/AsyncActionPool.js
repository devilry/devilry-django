Ext.define('devilry.extjshelpers.AsyncActionPool', {
    singleton: true,
    config: {
        size: 20
    },

    constructor: function(config) {
        this.initConfig(config);
        this._occupants = 0;
    },

    add: function(options) {
        this._run(options);
    },

    _run: function(options) {
        if(this._occupants > this.size) {
            Ext.defer(function() {
                this._run(options);
            }, 250, this);
            return;
        }
        //console.log('Running', this._occupants);
        this._occupants ++;
        Ext.bind(options.callback, options.scope, options.args, true)(this);
    },

    notifyTaskCompleted: function() {
        this._occupants --;
        //console.log('completed', this._occupants);
    }
});
