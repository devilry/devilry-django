Ext.define('devilry_qualifiesforexam_select.view.SelectQualifiedStudentsGrid', {
    extend: 'devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewGridBase',
    alias: 'widget.selectqualifiedstudentsgrid',
    store: 'AggregatedRelatedStudentInfos',
    title: gettext('Select students that qualify for final exams'),

    requires: [
        'devilry_extjsextras.PrimaryButton'
    ],

    firstAssignmentColumnIndex: 2, // NOTE: One row extra for the checkboxes
    hide_searchfield: true, // Hide searchfield because searching deselects - ctrl-f should work

    initComponent: function() {
        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            mode: 'simple'
        });
        this.callParent(arguments);
    },

    setupToolbar: function() {
        this.callParent(arguments);
        //this.bbar = undefined;
    }

    //updateCounter:function () {
        //// NOTE: We override this to stop the superclass from adding stuff to the bbar that we have hidden.
    //}
});

