Ext.define('devilry_subjectadmin.view.passedpreviousperiod.GridBase', {
    extend: 'Ext.grid.Panel',
    requires: [
        'Ext.XTemplate'
    ],

    store: 'PassedPreviousPeriodItems',
    border: 1,
    frame: false,
    hideHeaders: true,

    col1Tpl: [
        '<div class="groupinfo groupinfo_{id}" style="white-space:normal !important;">',
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
        '<div class="oldgroup_or_ignoredinfo oldgroup_or_ignoredinfo_{id}" style="white-space:normal !important;">',
            '<tpl if="oldgroup">',
                '<span class="oldgroupinfo text-success">',
                    gettext('Passed {oldperiodname}.'),
                '</span>',
            '<tpl else>',
                '<span class="text-warning">',
                    '<tpl switch="whyignored">',
                        '<tpl case="has_alias_feedback">',
                            gettext('Is already marked as previously passed.'),
                        '<tpl case="only_failing_grade_in_previous">',
                            gettext('The student has delivered this assignment previously, but never achieved a passing grade.'),
                        '<tpl case="has_feedback">',
                            gettext('Group has feedback for this assignment.'),
                    '</tpl>',
                '</span>',
            '</tpl>',
        '</div>'
    ],

    initComponent: function() {
        this.col1TplCompiled = Ext.create('Ext.XTemplate', this.col1Tpl);
        this.col2TplCompiled = Ext.create('Ext.XTemplate', this.col2Tpl);
        Ext.apply(this, {
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
            id: group.id,
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
            id: record.get('group').id,
            oldgroup: oldgroup,
            oldperiodname: oldgroup? oldgroup.period.long_name: null,
            whyignored: whyignored
        });
    }
});
