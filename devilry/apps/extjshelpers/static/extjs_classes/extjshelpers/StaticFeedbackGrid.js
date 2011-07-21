/** Panel to show a grid of StaticFeedbacks:
 *
 * @xtype staticfeedbackgrid
 */
Ext.define('devilry.extjshelpers.StaticFeedbackGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.staticfeedbackgrid',
    cls: 'widget-staticfeedbackgrid',
    title: 'Feedbacks',
    hideHeaders: true,

    rowTpl: Ext.create('Ext.XTemplate',
        '{save_timestamp:date} <em>({grade})</em>'
    ),

    columns: [{
        header: 'Data',
        dataIndex: 'grade',
        flex: 1,
        renderer: function(value, metaData, staticfeedback) {
            return this.rowTpl.apply(staticfeedback.data);
        }
    }]
});
