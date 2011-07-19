/** Panel to show StaticFeedback info:
 *
 * @xtype staticfeedbackinfo
 */
Ext.define('devilry.extjshelpers.StaticFeedbackInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.staticfeedbackinfo',
    title: 'Feedback',
    cls: 'widget-staticfeedbackinfo',
    tpl: Ext.create('Ext.XTemplate',
        '<table class="verticalinfotable">',
        '   <tr>',
        '       <th>Grade</th>',
        '       <td>{grade}</td>',
        '   </tr>',
        '       <th>Points</th>',
        '       <td>{points}</td>',
        '   </tr>',
        '       <th>Is passing grade?</th>',
        '       <td>{is_passing_grade}</td>',
        '   </tr>',
        '</table>',
        '<div class="rendered_view">{rendered_view}<div>'
    ),

    initComponent: function() {
        this.callParent(arguments);
    },

    setStaticFeedback: function(feedback) {
        console.log(feedback);
        this.update(this.tpl.apply(feedback));
    }
});
