Ext.define('devilry.statistics.LabelManager', {
    extend: 'Ext.util.Observable',
    
    config: {
        loader: undefined
    },
    application_id: 'devilry.statistics.Labels',

    constructor: function(config) {
        this.initConfig(config);
        this.addEvents({
            "changedMany": true
        });
        this.callParent(arguments);
    },

    _onErrors: function(what) {
        Ext.MessageBox.show({
            title: Ext.String.format('Failed to {0} labels', what),
            msg: '<p>This is usually caused by an unstable server connection. <strong>Please re-try to save labels</strong>.</p>',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    },

    _onFinished: function() {
        Ext.getBody().unmask();
        window.location.href = window.location.href;
    },
    
    _changeRequired: function(student, match, label) {
        var labelRecord = student.labels[label];
        var has_label = labelRecord !== undefined; 
        if(match && !has_label) {
            return 'create';
        } else if(!match && has_label) {
            return 'delete';
        } else {
            return false;
        }
    },

    _sendRestRequest: function(args) {
        Ext.apply(args, {
            url: Ext.String.format('{0}/administrator/restfulsimplifiedrelatedstudentkeyvalue/', DevilrySettings.DEVILRY_URLPATH_PREFIX),
        });
        Ext.Ajax.request(args);
    },

    _create: function(toBeCreated) {
        if(toBeCreated.length === 0) {
            this._onFinished();
            return;
        };
        Ext.getBody().mask('Creating labels', 'page-load-mask');
        this._sendRestRequest({
            params: Ext.JSON.encode(toBeCreated),
            method: 'POST',
            scope: this,
            callback: function(op, success, response) {
                if(success) {
                    this._onFinished();
                } else {
                    this._onError('create');
                }
            }
        });
    },

    _delete: function(toBeDeleted, toBeCreated) {
        if(toBeDeleted.length === 0) {
            this._create(toBeCreated);
            return;
        };
        Ext.getBody().mask('Deleting current labels', 'page-load-mask');
        this._sendRestRequest({
            params: Ext.JSON.encode(toBeDeleted),
            method: 'DELETE',
            scope: this,
            callback: function(op, success, response) {
                if(success) {
                    this._create(toBeCreated);
                } else {
                    this._onError('delete');
                }
            }
        });
    },

    _createLabelObj: function(student, label, student_can_read) {
        return {
            relatedstudent: student.relatedStudentRecord.get('id'),
            application: this.application_id,
            key: label,
            student_can_read: (student_can_read == true)
        };
    },

    _addToAppropriateChagelist: function(toBeCreated, toBeDeleted, match, student, label, student_can_read) {
        var changeRequired = this._changeRequired(student, match, label);
        if(changeRequired === 'create') {
            toBeCreated.push(this._createLabelObj(student, label, student_can_read));
        } else if(changeRequired === 'delete') {
            var labelRecord = student.labels[label];
            toBeDeleted.push(labelRecord.get('id'));
        }
    },

    setLabels: function(options) {
        var labelRecords = [];
        Ext.getBody().mask('Updating labels', 'page-load-mask');
        this.loader.clearFilter();

        var toBeCreated = [];
        var toBeDeleted = [];
        Ext.each(this.loader.store.data.items, function(student) {
            var match = Ext.bind(options.filter, options.scope)(student);
            this._addToAppropriateChagelist(toBeCreated, toBeDeleted, match, student, options.label, options.student_can_read);
            this._addToAppropriateChagelist(toBeCreated, toBeDeleted, !match, student, options.negative_label, options.student_can_read);
        }, this);
        this._delete(toBeDeleted, toBeCreated);
    }
});
