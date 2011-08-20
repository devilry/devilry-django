/** AssignmentGroup details panel.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupDetails', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgroupdetails',
    cls: 'widget-assignmentgroupdetails',

    tpl: Ext.create('Ext.XTemplate',
        // TODO !is_open without any published feedback and perhaps with failing grade?
        '<tpl if="is_open">',
        '    <section class="info-small">',
        '       <h1>Open</h1>',
        '       <p>This group is <em>open</em>. A group should remain open until you have finished grading them, and Devilry normally opens and closes groups for you automatically. You may want to manually close a group, using <span class="menuref">Close group</span> in the toolbar, if you want to make the current grade their final grade on this assignment. A closed group can be re-opened at any time.</p>',
        '    </section>',
        '</tpl>',
        '<tpl if="!is_open">',
        '    <section class="ok-small">',
        '       <h1>Closed</h1>',
        '       <p>This group is <em>closed</em>. This usually means that a group has been corrected and given feedback. A closed group can be re-opened at any time using <span class="menuref">Open group</span> in the toolbar.</p>',
        '    </section>',
        '</tpl>',
        '<tpl if="numDeliveries == 0">',
        '    <section class="warning-small">',
        '       <h1>No deliveries</h1>',
        '       <p>This group has no deliveries.</p>',
        '    </section>',
        '</tpl>'
    ),

    initComponent: function() {
        Ext.apply(this, {
            
        });
        this.callParent(arguments);
    }
});
