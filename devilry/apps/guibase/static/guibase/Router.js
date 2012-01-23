Ext.define('guibase.Router', {
    extend: 'Ext.util.Observable',
    requires: [
        'Ext.util.History'
    ],

    constructor: function(handler) {
        this.handler = handler;
        this.routes = [];
        this.started = false;
        this.callParent();
    },

    add: function(regex, action) {
        if(!Ext.typeOf(regex, 'regex')) {
            throw 'pattern must be regex.'
        }
        this.routes.push({
            regex: regex,
            action: action
        });
    },

    start: function() {
        if(this.started) {
            throw "Can only start() once!";
        }
        this.started = true;
        this._initHistory();
    },

    _trigger: function(token) {
        for(var index in this.routes) {
            var route = this.routes[index];
            var match = token.match(route.regex);
            if(match) {
                var args = match.slice(1);
                Ext.bind(this.handler[route.action], this.handler, args, true)(route.action);
                return;
            }
        }
        Ext.bind(this.handler['routeNotFound'], this.handler)();
    },

    _initHistory: function() {
        Ext.getBody().createChild({
            tag: 'form',
            id: 'history-form' ,
            cls: Ext.baseCSSPrefix + 'hide-display',
            html: [
                '<input type="hidden" id="', Ext.util.History.fieldId, '" />',
                '<iframe id="', Ext.util.History.iframeId, '"></iframe>'
            ].join('')
		});
		Ext.util.History.init(this._onHistoryReady, this);
    },

    _onHistoryReady: function(history) {
        this.mon(Ext.util.History, 'change', this._onHistoryChange, this);
        var token = history.getToken();
        if(token == null) {
            token = '';
        }
        this._trigger(token);
    },

    _onHistoryChange: function(token) {
        this._trigger(token);
    }
});
