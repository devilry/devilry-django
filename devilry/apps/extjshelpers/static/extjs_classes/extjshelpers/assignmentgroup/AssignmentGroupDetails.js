/** AssignmentGroup details panel.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupDetails', {
    extend: 'devilry.extjshelpers.SingleRecordView',
    alias: 'widget.assignmentgroupdetails',
    cls: 'widget-assignmentgroupdetails',

    tpl: Ext.create('Ext.XTemplate',
        // TODO !is_open without any published feedback and perhaps with failing grade?
        '<tpl if="canExamine">',
        '    <tpl if="is_open">',
        '        <div class="section info-small">',
        '           <h1>Open</h1>',
        '           <p>This group is <em>open</em>. A group should remain open until you have finished grading them, and Devilry normally opens and closes groups for you automatically. You may want to manually close a group, using <span class="menuref">Close group</span> in the toolbar, if you want to make the current grade their final grade on this assignment. A closed group can be re-opened at any time.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="!is_open">',
        '        <div class="section ok-small">',
        '           <h1>Closed</h1>',
        '           <p>This group is <em>closed</em>. This means that a group has been corrected and given feedback. If the group has not been given feedback, a closed group signals that this group will not get any correction on this assignment. A closed group can be re-opened at any time using <span class="menuref">Open group</span> in the toolbar.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="numDeliveries == 0">',
        '        <div class="section warning-small">',
        '           <h1>No deliveries</h1>',
        '           <p>This group has no deliveries.</p>',
        '        </div>',
        '    </tpl>',
        '</tpl>',
        '<tpl if="!canExamine">',
        '    <tpl if="is_open">',
        '        <div class="section info-small">',
        '           <h1>Open</h1>',
        '           <p>This assignment is open for more deliveries. You can add as many deliveries as you like, and your examiner(s) will normally correct your latest delivery.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="!is_open">',
        '        <div class="section ok-small">',
        '           <h1>Closed</h1>',
        '           <p>This assignment is <em>closed</em>. This usually means that you have been given feedback, and that the latest feedback is your final grade on this assignment. If you have not been given feedback, and you think this is wrong, you should contact your examiner or course administrator.</p>',
        '        </div>',
        '    </tpl>',
        '    <tpl if="numDeliveries == 0">',
        '        <div class="section warning-small">',
        '           <h1>No deliveries</h1>',
        '           <p>You have no deliveries on this assignment.</p>',
        '        </div>',
        '    </tpl>',
        '</tpl>'
    ),

    initComponent: function() {
        Ext.apply(this, {
            
        });
        this.callParent(arguments);
    }
});
