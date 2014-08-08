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

    _onError: function(what, response) {
        Ext.getBody().unmask();
        var httperror = 'Lost connection with server';
        if(response.status !== 0) {
            httperror = Ext.String.format('{0} {1}', response.status, response.statusText);
        }
        Ext.MessageBox.show({
            title: Ext.String.format('Failed to {0} labels', what),
            msg: '<p>This is usually caused by an unstable server connection. <strong>Please re-try saving labels</strong>.</p>' +
                Ext.String.format('<p>Error details: {0}</p>', httperror),
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    },

    _onFinished: function() {
        Ext.getBody().unmask();
        window.location.search = 'open_students=yes';
    },
    
    _changeRequired: function(student, match, label) {
        var has_label = student.hasLabel(label);
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
            url: Ext.String.format('{0}/administrator/restfulsimplifiedrelatedstudentkeyvalue/', DevilrySettings.DEVILRY_URLPATH_PREFIX)
        });
        Ext.Ajax.request(args);
    },

    _create: function(toBeCreated) {
        if(toBeCreated.length === 0) {
            this._onFinished();
            return;
        }
        Ext.getBody().mask('Creating labels', 'page-load-mask');
        this._sendRestRequest({
            params: Ext.JSON.encode(toBeCreated),
            method: 'POST',
            scope: this,
            callback: function(op, success, response) {
                if(success) {
                    this._onFinished();
                } else {
                    this._onError('create', response);
                }
            }
        });
    },

    _delete: function(toBeDeleted, toBeCreated) {
        if(toBeDeleted.length === 0) {
            this._create(toBeCreated);
            return;
        }
        Ext.getBody().mask('Deleting current labels', 'page-load-mask');
        this._sendRestRequest({
            params: Ext.JSON.encode(toBeDeleted),
            method: 'DELETE',
            scope: this,
            callback: function(op, success, response) {
                if(success) {
                    this._create(toBeCreated);
                } else {
                    this._onError('delete', response);
                }
            }
        });
    },

    _createLabelObj: function(student, label, student_can_read) {
        return {
            relatedstudent: student.get('relatedstudent_id'),
            application: this.application_id,
            key: label,
            student_can_read: (student_can_read === true)
        };
    },

    _addToAppropriateChagelist: function(toBeCreated, toBeDeleted, match, student, label, student_can_read) {
        var changeRequired = this._changeRequired(student, match, label);
        if(changeRequired === 'create') {
            toBeCreated.push(this._createLabelObj(student, label, student_can_read));
        } else if(changeRequired === 'delete') {
            var labelId = student.getLabelId(label);
            if(labelId === -1) {
                throw "Label not found";
            }
            toBeDeleted.push(labelId);
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
