/**
 * A panel that displays information about a single group.
 */
Ext.define('subjectadmin.view.managestudents.SingleGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'singlegroupview',
    ui: 'transparentpanel',

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
