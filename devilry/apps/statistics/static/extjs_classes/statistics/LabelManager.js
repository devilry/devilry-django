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
        this._watingFor = this.loader.store.count();
        Ext.each(this.loader.store.data.items, function(student) {
            var match = Ext.bind(options.filter, options.scope)(student);
            var labelRecord = student.get('labels')[options.label];
            var has_label = labelRecord !== undefined; 
            //console.log(student.get('labels'), labelRecord, has_label, options.label, match);
            if(match && !has_label) {
                this._createLabel(student, options.label, index);
            } else if(!match && has_label) {
                this._deleteLabel(student, labelRecord, index);
            } else {
                this._checkFinished();
            }
            index ++;
        }, this);
    },

    _createLabel: function(student, label, index) {
        var record = this._createLabelRecord(student, label);
        devilry.extjshelpers.AsyncActionPool.add({
            scope: this,
            callback: function(pool) {
                record.save({
                    scope: this,
                    callback: function(records, op, successful) {
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}', index));
                        var label = record.get('key');
                        //student.get('labels')[label] = record;
                        student.setLabel(label, record);
                        pool.notifyTaskCompleted();
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
                    callback: function() {
                        Ext.getBody().mask(Ext.String.format('Completed updating label {0}', index));
                        var label = record.get('key');
                        //delete student.get('labels')[label];
                        student.delLabel(label);
                        pool.notifyTaskCompleted();
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
            this._watingFor = undefined;
            Ext.getBody().unmask();
            this.fireEvent('changedMany');
        }
    },

    _createLabelRecord: function(student, label) {
        var record = Ext.create('devilry.apps.administrator.simplified.SimplifiedRelatedStudentKeyValue', {
            relatedstudent: student.get('relatedstudent').get('id'),
            application: this.application_id,
            key: label
        });
        return record;
    },
});
