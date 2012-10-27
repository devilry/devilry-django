Ext.define('devilry_subjectadmin.view.passedpreviousperiod.SelectGroupsGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.selectpassedpreviousgroupsgrid',
    cls: 'devilry_subjectadmin_selectpassedpreviousgroupssgrid bootstrap',
    requires: [
        'Ext.XTemplate',
        'devilry_extjsextras.GridBigButtonCheckboxModel'
    ],

    store: 'PassedPreviousPeriodItems',
    border: 1,
    frame: false,
    hideHeaders: true,

    col1Tpl: [
        '<div class="groupinfo groupinfo_{id}">',
            '<div class="names"><strong>',
                '{displaynames}',
            '</strong></div>',
            '<tpl if="name">',
                '<div class="groupname">{name}</div>',
            '</tpl>',
            '<div class="username"><small>{usernames}</small></div>',
        '</div>'
    ],

    col2Tpl: [
        '<div class="oldgroupinfo oldgroupinfo_{id}">',
            '<tpl if="oldgroup">',
                '<span class="label label-success">',
                    '{oldgroup.period.short_name}.{oldgroup.assignment.short_name}',
                '</span>',
            '</tpl>',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        this.col2TplCompiled = Ext.create('Ext.XTemplate', this.col2Tpl);
        Ext.apply(this, {
            selModel: Ext.create('devilry_extjsextras.GridBigButtonCheckboxModel'),
            columns: [{
                dataIndex: 'id',
                flex: 7,
                menuDisabled: true,
                renderer: this.renderCol1,
                sortable: false
            }, {
                dataIndex: 'id',
                flex: 3,
                menuDisabled: true,
                renderer: this.renderCol2,
                sortable: false
            }],
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
                    text: interpolate(gettext('Autodetected with passing grade in previous %(period_term)s'), {
                        period_term: gettext('period')
                    }, true),
                    listeners: {
                        scope: this,
                        click: this._onSelectPassingGradeInPreviousPeriod
                    }
                }]
            }]
        });
        this.callParent(arguments);
    },

    renderCol1: function(unused, unused2, record) {
        var group = record.get('group');
        var displaynames = [];
        var usernames = [];
        var no_fullnames = true;
        for(var index=0; index<group.candidates.length; index++)  {
            var candidate = group.candidates[index];
            if(!Ext.isEmpty(candidate.full_name)) {
                no_fullnames = false;
            }
            displaynames.push(candidate.user.displayname);
            usernames.push(candidate.user.username);
        }
        return this.col1TplCompiled.apply({
            id: record.get('id'),
            name: group.name,
            displaynames: displaynames.join(', '),
            usernames: usernames.join(', '),
            no_fullnames: no_fullnames
        });
    },

    renderCol2: function(unused, unused2, record) {
        var oldgroup = record.get('oldgroup');
        var whyignored = record.get('whyignored');
        return this.col2TplCompiled.apply({
            id: record.get('id'),
            oldgroup: oldgroup,
            whyignored: whyignored
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
