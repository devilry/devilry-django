Ext.define('devilry_extjsextras.Router', {
    mixins: {
        observable: 'Ext.util.Observable'
    },
    requires: [
        'Ext.util.History'
    ],

    namedParam: /:\w+/g,
    splatParam: /\*\w+/g,
    escapeRegExp: /[-[\]{}()+?.,\\^$|#\s]/g,

    constructor: function(handler, config) {
        this.handler = handler;
        this.routes = [];
        this.started = false;
        this.eventsSuspended = false;

        this.mixins.observable.constructor.call(this, config);
        this.addEvents(
            /**
             * @event
             * Fired before a successful route.
             * @param route The Route object.
             * @param routeInfo The route info object (the same that is sent to the handlers).
             */
            'beforeroute',

            /**
             * @event
             * Fired after a successful route.
             * @param route The Route object.
             * @param routeInfo The route info object (the same that is sent to the handlers).
             */
            'afterroute'
        );
    },

    add: function(pattern, action) {
        var regex;
        if(Ext.typeOf(pattern) == 'regexp') {
            regex = pattern;
        } else if(Ext.typeOf(pattern) == 'string') {
            regex = this._patternToRegExp(pattern);
        } else {
            throw 'pattern must be regex.';
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
        if(this.eventsSuspended) {
            this.eventsSuspended = false;
            return;
        }
        if(token == null) {
            token = '';
        }
        var routeInfo = {
            token: token,
            url: '#' + token
        };
        for(var index in this.routes) {
            var route = this.routes[index];
            var match = token.match(route.regex);
            if(match) {
                var args = match.slice(1);
                this.fireEvent('beforeroute', this, routeInfo);
                Ext.bind(this.handler[route.action], this.handler, args, true)(Ext.apply(routeInfo, {
                    action: route.action
                }));
                this.fireEvent('afterroute', this, routeInfo);
                return;
            }
        }
        Ext.bind(this.handler['routeNotFound'], this.handler)(Ext.apply(routeInfo, {
            action: 'routeNotFound'
        }));
    },

    _initHistory: function() {
		Ext.util.History.init(this._onHistoryReady, this);
    },

    _onHistoryReady: function(history) {
        this.resume();
        var token = history.getToken();
        if(token == null) {
            token = '';
        }
        this._trigger(token);
    },

    _onHistoryChange: function(token) {
        this._trigger(token);
    },

    suspend: function() {
        this.mun(Ext.util.History, 'change', this._onHistoryChange, this);
    },

    resume: function() {
        this.mon(Ext.util.History, 'change', this._onHistoryChange, this);
    },
    startOrResume: function() {
        if(this.started) {
            this.resume();
        } else {
            this.start();
        }
    },

    /**
     * @private
     * Convert a route string into a regular expression, suitable for matching
     * against the current location hash.
     */
    _patternToRegExp: function(pattern) {
        var regex = pattern.replace(this.escapeRegExp, '\\$&');
        regex = regex.replace(this.namedParam, '([^\/]*)');
        regex = regex.replace(this.splatParam, '(.*?)');
        return new RegExp('^' + regex + '$');
    },

    /**
     * Remove a prefixed ``#`` from ``token`` if present, or just return the unchanged token.
     */
    normalizeToken: function(token) {
        if(token.length > 0 && token.charAt(0) == '#') {
            return token.substring(1);
        } else {
            return token;
        }
    },

    _navigate: function(token, ignoreDuplicate, suspendEvents) {
        token = this.normalizeToken(token);
        if(ignoreDuplicate && token == Ext.util.History.getToken()) {
            return;
        }
        if(suspendEvents) {
            this.eventsSuspended = true;
        }
        Ext.util.History.add(token);
    },

    /**
     * @param token The token to navigate to. ``token`` is filtered through #normalizeToken.
     * @param ignoreDuplicate Do nothing if the normalized token matches the current token.
     */
    navigate: function(token, ignoreDuplicate) {
        this._navigate(token, ignoreDuplicate);
    },

    /**
     * Set token without triggering the routing events.
     * Use this if you just want to update the URL, but not navigate to the
     * updated URL.
     */
    setHashWithoutEvent: function(token) {
        this._navigate(token, true, true);
    }
});
