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
        deliveryid: undefined
    },

    constructor: function(config) {
        this.addEvents('afterStoreLoad');
        return this.callParent([config]);
    },
    
    initComponent: function() {
        this.callParent(arguments);

        var me = this;
        var staticfeedbackstoreid = 'devilry.apps.examiner.simplified.SimplifiedStaticFeedbackStore';
        var staticfeedbackstore = Ext.data.StoreManager.lookup(staticfeedbackstoreid);
        this.store = staticfeedbackstore;
        this.store.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        this.store.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery',
            comp: 'exact',
            value: this.deliveryid
        }]);

        this.storeLoadedOnce = false;
        this.feedbackSelector = Ext.create('Ext.form.field.ComboBox', {
            store: this.store,
            displayField: 'save_timestamp',
            valueField: 'id',
            autoSelect: true,
            width: 320,
            forceSelection: true,
            hidden: true,
            editable: false,

            listeners: {
                select: function(field, staticfeedbackrecord) {
                    me.setStaticFeedback(staticfeedbackrecord[0].data);
                }
            }
        });

        this.addListener('render', function() { // Header is not available until it is rendered
            me.getHeader().add(this.feedbackSelector);
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
                        me.bodyWithNoFeedback();
                    }
                    else {
                        var first = records[0].data;
                        if(records.length > 1) {
                            me.feedbackSelector.setRawValue(first.save_timestamp);
                            me.feedbackSelector.show();
                        } else {
                            me.feedbackSelector.hide();
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
        this.setBody({
            xtype: 'component',
            cls: this.cls + '-feedbackview',
            html: this.tpl.apply(feedback)
        });
    },

    setBody: function(content) {
        this.removeAll();
        this.add(content);
    },

    bodyWithNoFeedback: function() {
        this.setBody({
            xtype: 'component',
            cls: 'no-feedback',
            html: 'No feedback yet'
        });
    }
});
