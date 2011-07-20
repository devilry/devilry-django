/** Panel to show StaticFeedback info.
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

    config: {
        store: undefined
    },

    constructor: function(config) {
        this.addEvents('afterStoreLoad');
        return this.callParent([config]);
    },
    
    initComponent: function() {
        this.callParent(arguments);

        var me = this;
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);

        this.storeLoadedOnce = false;
        this.feedbackSelector = Ext.create('Ext.form.field.ComboBox', {
            //fieldLabel: 'history',
            store: this.store,
            displayField: 'save_timestamp',
            valueField: 'id',
            autoSelect: true,
            width: 320,
            forceSelection: true,
            editable: false,

            listeners: {
                select: function(field, staticfeedbackrecord) {
                    me.setStaticFeedback(staticfeedbackrecord[0].data);
                }
            }
        });

        this.feedbackView = Ext.create('Ext.container.Container', {
            cls: this.cls + '-feedbackview'
        });

        this.loadStore();
    },

    loadStore: function() {
        var me = this;
        this.store.load({
            callback: function(records, operation, successful) {
                if(successful) {
                    if(records.length == 0) {
                    }
                    else {
                        var first = records[0].data;
                        var header = me.getHeader();
                        if(records.length > 1) {
                            if(!me.storeLoadedOnce) {
                                header.add(me.feedbackSelector);
                            }
                            me.feedbackSelector.setRawValue(first.save_timestamp);
                        }
                        me.setStaticFeedback(first);
                        me.fireEvent('afterStoreLoad');
                        me.storeLoadedOnce = true;
                    }
                }
            }
        });
    },

    loadFeedbackViewer: function() {
        this.loadStore();
    },

    getHeader: function() {
        return this.dockedItems.items[0];
    },

    setStaticFeedback: function(feedback) {
        this.removeAll();
        this.add({
            xtype: 'component',
            cls: this.cls + '-feedbackview',
            html: this.tpl.apply(feedback)
        });
    },
});
