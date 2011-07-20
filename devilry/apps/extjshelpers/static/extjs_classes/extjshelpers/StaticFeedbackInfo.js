/** Panel to show StaticFeedback info:
 *
 * @xtype staticfeedbackinfo
 */
Ext.define('devilry.extjshelpers.StaticFeedbackInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.staticfeedbackinfo',
    cls: 'widget-staticfeedbackinfo',
    title: 'Feedback',

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
        '   </tr>',
        '       <th>Feedback save time</th>',
        '       <td>{save_timestamp:date}</td>',
        '   </tr>',
        '</table>',
        '<div class="rendered_view">{rendered_view}<div>'
    ),

    
    initComponent: function() {
        var me = this;
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        //this.store.load();

        var feedbackSelector = Ext.create('Ext.form.field.ComboBox', {
            fieldLabel: 'Feedback history',
            store: this.store,
            displayField: 'save_timestamp',
            valueField: 'id',
            autoSelect: true,
            width: 440,
            forceSelection: true,
            editable: false,

            listeners: {
                select: function(field, staticfeedbackrecord) {
                    me.setStaticFeedback(staticfeedbackrecord[0].data);
                }
            }
        });

        Ext.apply(this, {
            tbar: [feedbackSelector]
        });
        this.callParent(arguments);

        this.store.load({
            callback: function(records, operation, successful) {
                if(successful) {
                    var first = records[0].data;
                    feedbackSelector.setRawValue(first.save_timestamp);
                    me.setStaticFeedback(first);
                }
            }
        });
    },

    setStaticFeedback: function(feedback) {
        this.update(this.tpl.apply(feedback));
    }
});
