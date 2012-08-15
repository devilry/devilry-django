Ext.define('devilry_student.view.browsehistory.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.browsehistory',
    cls: 'devilry_student_browsehistory',

    /**
     * @cfg {string} [period_id]
     * ID of a period that should be selected on load.
     */

    frame: false,
    border: 0,
    bodyPadding: 20,
    autoScroll: true,
    layout: 'fit',

    items: [{
        xtype: 'student-browseperiods',
        urlCreateFn: function(groupRecord) {
            //return Ext.String.format('{0}/student/assignmentgroup/{1}',
                //DevilrySettings.DEVILRY_URLPATH_PREFIX, groupRecord.get('id'));
            return Ext.String.format('#/group/{0}/', groupRecord.get('id'));

        }
    }]
});
