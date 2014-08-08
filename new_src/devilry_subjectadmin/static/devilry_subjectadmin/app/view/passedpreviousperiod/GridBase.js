Ext.define('devilry_subjectadmin.view.passedpreviousperiod.GridBase', {
    extend: 'Ext.grid.Panel',
    requires: [
        'Ext.XTemplate'
    ],

    store: 'PassedPreviousPeriodItems',
    border: 1,
    frame: false,
    hideHeaders: true,

    groupInfoColTpl: [
        '<div class="groupinfo groupinfo_{id}" style="white-space:normal !important;">',
            '<div class="names"><strong>',
                '{displaynames}',
            '</strong></div>',
            '<tpl if="name">',
                '<div class="groupname">{name}</div>',
            '</tpl>',
            '<div class="usernames"><small class="muted">{usernames}</small></div>',
        '</div>'
    ],

    oldOrIgnoredColTpl: [
        '<div class="oldgroup_or_ignoredinfo oldgroup_or_ignoredinfo_{id}" style="white-space:normal !important;">',
            '<tpl if="oldgroup">',
                '<span class="oldgroupinfo text-success">',
                    gettext('Passed {oldperiodname}.'),
                '</span>',
            '<tpl else>',
                '<span class="whyignored whyignored_{whyignored} text-warning">',
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
        this.groupInfoColTplCompiled = Ext.create('Ext.XTemplate', this.groupInfoColTpl);
        this.oldOrIgnoredColTplCompiled = Ext.create('Ext.XTemplate', this.oldOrIgnoredColTpl);
        Ext.apply(this, {
            viewConfig:{
                markDirty:false
            },
            columns: [{
                dataIndex: 'id',
                text: gettext('Group'),
                flex: 7,
                menuDisabled: true,
                renderer: this.rendergroupInfoCol,
                sortable: false
            }]
        });
        this.extraInit();
        this.callParent(arguments);
    },

    extraInit: function () {
    },

    rendergroupInfoCol: function(unused, unused2, record) {
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
        return this.groupInfoColTplCompiled.apply({
            id: group.id,
            name: group.name,
            displaynames: displaynames.join(', '),
            usernames: usernames.join(', '),
            no_fullnames: no_fullnames
        });
    },

    renderOldOrIgnoredCol: function(unused, unused2, record) {
        var oldgroup = record.get('oldgroup');
        var whyignored = record.get('whyignored');
        return this.oldOrIgnoredColTplCompiled.apply({
            id: record.get('group').id,
            oldgroup: oldgroup,
            oldperiodname: oldgroup? oldgroup.period.long_name: null,
            whyignored: whyignored
        });
    }
});
