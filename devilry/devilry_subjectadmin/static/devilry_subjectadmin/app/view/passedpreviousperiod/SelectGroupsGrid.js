Ext.define('devilry_subjectadmin.view.passedpreviousperiod.SelectGroupsGrid', {
    extend: 'devilry_subjectadmin.view.passedpreviousperiod.GridBase',
    alias: 'widget.selectpassedpreviousgroupsgrid',
    cls: 'devilry_subjectadmin_selectpassedpreviousgroupssgrid bootstrap',
    requires: [
        'devilry_extjsextras.GridBigButtonCheckboxModel'
    ],

    initComponent: function() {
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),
            tbar: [{
                text: gettext('Select'),
                menu: [{
                    text: gettext('Select all'),
                    listeners: {
                        scope: this,
                        click: this._onSelectAll
                    }
                }, {
                    text: gettext('Deselect all'),
                    listeners: {
                        scope: this,
                        click: this._onDeSelectAll
                    }
                }, '-', {
                    text: gettext('Autodetected as previously passed'),
                    listeners: {
                        scope: this,
                        click: this._onSelectPassingGradeInPreviousPeriod
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    extraInit: function () {
        this.columns.push({
            dataIndex: 'id',
            flex: 3,
            menuDisabled: true,
            renderer: this.renderOldOrIgnoredCol,
            sortable: false
        });
    },

    _onSelectAll: function() {
        this.getSelectionModel().selectAll();
    },
    _onDeSelectAll: function() {
        this.getSelectionModel().deselectAll();
    },

    _onSelectPassingGradeInPreviousPeriod: function() {
        this.selectWithPassingGradeInPrevious();
    },

    selectWithPassingGradeInPrevious: function() {
        var records = [];
        this.getStore().each(function(record) {
            if(record.get('oldgroup') !== null) {
                records.push(record);
            }
        });
        this.getSelectionModel().select(records);
    }
});
