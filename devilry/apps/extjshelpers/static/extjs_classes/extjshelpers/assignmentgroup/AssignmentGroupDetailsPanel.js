/** AssignmentGroup details panel.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupDetailsPanel', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgroupdetailspanel',
    cls: 'widget-assignmentgroupdetailspanel',

    tpl: Ext.create('Ext.XTemplate',
        '<dl>',
        '   <dt>Id</dt>',
        '   <dd>{id}</dd>',
        '   <dt>Is open?</dt>',
        '   <dd>{is_open}</dd>',
        '</dl>'
    )
});
