/** AssignmentGroup details panel.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupDetailsPanel', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.assignmentgroupdetailspanel',
    cls: 'widget-assignmentgroupdetailspanel',

    config: {
        /**
        * @cfg
        * AssignmentGroup object such as the ``data`` attribute of a record
        * returned from loading from a store. (Required).
        */
        assignmentgroup: undefined
    },

    title: 'Assignment group',
    bodyTpl: Ext.create('Ext.XTemplate',
        '<dl>',
        '   <dt>Id</dt>',
        '   <dd>{id}</dd>',
        '   <dt>Is open?</dt>',
        '   <dd>{is_open}</dd>',
        '   <dt>Candidates</dt>',
        '   <dd>TODO</dd>',
        '</dl>'
    ),


    initComponent: function() {
        Ext.apply(this, {
            html: this.bodyTpl.apply(this.assignmentgroup)
        });
        this.callParent(arguments);
    },
});
