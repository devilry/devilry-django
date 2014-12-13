Ext.define('devilry_authenticateduserinfo.UserInfo', {
    singleton: true,
    requires: [
        'devilry_authenticateduserinfo.UserInfoModel'
    ],

    waitingForLoad: [],
    userInfoRecord: null,

    /**
     * Load UserInfo if required, or use the cached record.
     *
     * The first time this is called, the UserInfoModel is loaded.
     * While it is loading, callback functions are queued, and all
     * functions in the queue is called when the record is loaded.
     *
     * If the UserInfo record is already loaded, the callback function is
     * called at once.
     *
     * @param {Function} [fn=undefined]:
     *      Optional callback function. Called with the UserInfo record as
     *      first and only argument.
     * @param {Object} [scope=undefined]:
     *      Optional scope for ``fn``.
     */
    load: function(fn, scope) {
        if(this.userInfoRecord) {
            Ext.callback(fn, scope, [this.userInfoRecord]);
        } else {
            if(fn) {
                this.waitingForLoad.push({
                    fn: fn,
                    scope: scope
                });
            }
            if(this.loading) {
                return;
            }
            this.loading = true;
            devilry_authenticateduserinfo.UserInfoModel.load(null, {
                scope: this,
                success: function(record) {
                    this.userInfoRecord = record;
                    this.loading = false;
                    this._handleWaiting();
                },
                failure: this._onFailure
            });
        }
    },

    _handleWaiting: function() {
        Ext.Array.each(this.waitingForLoad, function(config) {
            Ext.callback(config.fn, config.scope, [this.userInfoRecord]);
        }, this);
        this.waitingForLoad = [];
    },

    _onFailure: function(unused, operation) {
        this.loading = false;
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: gettext('Failed to load infomation about the authenticated user. Try to reload the page.'),
            icon: Ext.MessageBox.ERROR
        });
    }
});
