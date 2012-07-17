Ext.define('devilry_subjectadmin.view.period.ManageRelatedStudentsPanel' ,{
    extend: 'devilry_subjectadmin.view.period.ManageRelatedUsersPanel',
    alias: 'widget.managerelatedstudentspanel',

    initComponent: function() {
        this.extraColumn = {
            header: 'Candidate ID',  dataIndex: 'candidate_id', flex: 1
        }
        this.callParent(arguments);
    },

    searchMatchesRecord: function(query, record) {
        var match = this.callParent(arguments);
        return match || this.caseIgnoreContains(record.get('candidate_id'), query);
    }
});
