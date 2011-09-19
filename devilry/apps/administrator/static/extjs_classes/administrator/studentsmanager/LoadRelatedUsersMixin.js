Ext.define('devilry.administrator.studentsmanager.LoadRelatedUsersMixin', {
    loadAllRelatedUsers: function(modelname, callback) {
        var relatedUserModel = Ext.ModelManager.getModel(modelname);

        var relatedUserStore = Ext.create('Ext.data.Store', {
            model: relatedUserModel,
            remoteFilter: true,
            remoteSort: true
        });

        relatedUserStore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'period',
            comp: 'exact',
            value: this.periodid
        }]);
        //deliverystore.proxy.extraParams.orderby = Ext.JSON.encode(['-deadline__deadline', '-number']);

        relatedUserStore.proxy.extraParams.page = 1;
        relatedUserStore.pageSize = 1;
        relatedUserStore.load({
            scope: this,
            callback: function(records) {
                relatedUserStore.proxy.extraParams.page = 1;
                relatedUserStore.pageSize = relatedUserStore.totalCount;
                relatedUserStore.load({
                    scope: this,
                    callback: callback
                });
            }
        });
    },

    postLoadAllRelatedUsers: function(callbackOpt, relatedUsers) {
        Ext.bind(
            callbackOpt.callback,
            callbackOpt.scope,
            callbackOpt.args,
            true
        )(relatedUsers);
    },

    relatedUserRecordsToArray: function(relatedUsers) {
        return Ext.Array.map(relatedUsers, function(relatedUser) {
            return Ext.String.trim(relatedUser.data.userspec);
        }, this);
    },


    loadAllRelatedStudents: function(callbackOpt) {
        if(this._relatedStudents == undefined) {
            this.getEl().mask('Loading related students');
            this._onLoadAllRelatedStudentsCallbackOpt = callbackOpt
            this.loadAllRelatedUsers(
                'devilry.apps.administrator.simplified.SimplifiedRelatedStudent',
                this.onLoadAllRelatedStudents
            );
        } else {
            this.postLoadAllRelatedUsers(callbackOpt, this._relatedStudents);
        };
    },

    onLoadAllRelatedStudents: function(records) {
        this.getEl().unmask();
        this._relatedStudents = records;
        this.postLoadAllRelatedUsers(this._onLoadAllRelatedStudentsCallbackOpt, records);
        this._onLoadAllRelatedStudentsCallbackOpt = undefined;
    },


    loadAllRelatedExaminers: function(callbackOpt) {
        if(this._relatedExaminers == undefined) {
            this.getEl().mask('Loading related students');
            this._onLoadAllRelatedExaminersCallbackOpt = callbackOpt
            this.loadAllRelatedUsers(
                'devilry.apps.administrator.simplified.SimplifiedRelatedExaminer',
                this.onLoadAllRelatedExaminers
            );
        } else {
            this.postLoadAllRelatedUsers(callbackOpt, this._relatedExaminers);
        };
    },

    onLoadAllRelatedExaminers: function(records) {
        this.getEl().unmask();
        this._relatedExaminers = records;
        this.postLoadAllRelatedUsers(this._onLoadAllRelatedExaminersCallbackOpt, records);
        this._onLoadAllRelatedExaminersCallbackOpt = undefined;
    }
});
