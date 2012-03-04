/**
 * A panel that displays information about a single group.
 */
Ext.define('subjectadmin.view.managestudents.SingleGroupView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'singlegroupview',

    /**
     * @cfg {subjectadmin.model.Group} groupRecord (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            html: 'hei ' + this.groupRecord.get('students')[0].student__username
        });
        this.callParent(arguments);
    }
});
