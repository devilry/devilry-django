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
    
    setLabels: function(options) {
        var labelRecords = [];
        Ext.getBody().mask('Updating labels');
        var index = 0;
        this._finished = 0;
        this._errors = 0;
        this.loader.clearFilter();
        this._watingFor = this.loader.store.count() * 2;
        Ext.each(this.loader.store.data.items, function(student) {
            var match = Ext.bind(options.filter, options.scope)(student);
            this._changeLabelIfRequired(student, match, options.label, options.student_can_read, index);
            index ++;
            this._changeLabelIfRequired(student, !match, options.negative_label, options.student_can_read, index);
            index ++;
        }, this);
    },

    _changeLabelIfRequired: function(student, match, label, student_can_read, index) {
        var labelRecord = student.get('labels')[label];
        var has_label = labelRecord !== undefined; 
        if(match && !has_label) {
            this._createLabel(student, label, student_can_read, index);
        } else if(!match && has_label) {
            this._deleteLabel(student, labelRecord, index);
        } else {
            this._checkFinished();
        }
    },

    _createLabel: function(student, label, student_can_read, index) {
        var record = this._createLabelRecord(student, label, student_can_read);
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.save({
                    scope: this,
                    callback: function(r, op) {
                        pool.notifyTaskCompleted();
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}/{1}', index, this._watingFor));
                        if(op.success) {
                            var label = record.get('key');
                            student.setLabel(label, record);
                        }
                        else {
                            this._errors ++;
                        }
                        this._checkFinished();
                    }
                });
            }
        });
    },

    _deleteLabel: function(student, record, index) {
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.destroy({
                    scope: this,
                    callback: function(r, op) {
                        pool.notifyTaskCompleted();
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}/{1}', index, this._watingFor));
                        if(op.success) {
                            var label = record.get('key');
                            student.delLabel(label);
                        }
                        else {
                            this._errors ++;
                        }
                        this._checkFinished();
                    }
                });
            }
        });
    },

    _checkFinished: function(dontAddToFinished) {
        if(!dontAddToFinished) {
            this._finished ++;
        }
        if(this._watingFor == undefined) {
            return;
        }
        if(this._finished >= this._watingFor) {
            this._onFinished();
        }
    },

    _onFinished: function() {
        Ext.getBody().unmask();
        this.fireEvent('changedMany');
        if(this._errors > 0) {
            this._onErrors();
        }
        this._watingFor = undefined;
    },

    _onErrors: function() {
        Ext.MessageBox.show({
            title: Ext.String.format('Failed to set {0} of {1} labels', this._errors, this._watingFor),
            msg: '<p>This is usually caused by an unstable server connection. <strong>Try to apply the labels again</strong>.</p>',
            buttons: Ext.Msg.OK,
            icon: Ext.Msg.ERROR,
            closable: false
        });
    },

    _createLabelRecord: function(student, label, student_can_read) {
        var record = Ext.create('devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue', {
            relatedstudent: student.get('relatedstudent').get('id'),
            application: this.application_id,
            key: label,
            student_can_read: (student_can_read == true)
        });
        return record;
    },
});
