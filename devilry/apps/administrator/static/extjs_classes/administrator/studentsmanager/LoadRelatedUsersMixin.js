Ext.define('devilry.administrator.studentsmanager.LoadRelatedUsersMixin', {
    loadAllRelatedUsers: function(modelname, callback) {
        var relatedUserModel = Ext.ModelManager.getModel(modelname);

        var relatedUserStore = Ext.create('Ext.data.Store', {
            model: relatedUserModel,
            remoteFilter: true,
            remoteSort: true
        });

        relatedUserStore.proxy.setDevilryFilters([{
            field: 'period',
            comp: 'exact',
            value: this.periodid
        }]);
        relatedUserStore.proxy.setDevilryResultFieldgroups(['user_details']);
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

    relatedUserRecordsToStringArray: function(relatedUsers, format) {
        var tpl = Ext.create('Ext.XTemplate', format);
        return Ext.Array.map(relatedUsers, function(relatedUser) {
            return tpl.apply(relatedUser.data);
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
        //console.log(records);
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
