/** Panel to show StaticFeedback info.
 *
 * @xtype staticfeedbackinfo
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.staticfeedbackinfo',
    cls: 'widget-staticfeedbackinfo',
    title: 'Feedback',

    config: {
        /**
         * @cfg Delivery id. (Required).
         */
        deliveryid: undefined,

        /**
         * @cfg {Ext.data.Store} FileMeta store. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
         * class.
         */
        staticfeedbackstore: undefined
    },

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
        '<tpl if="!isactive">',
        '   <div class="warning">',
        '       <strong>This is not the active feedback.</strong>',
        '       When an examiner publish a feedback, the feedback is ',
        '       stored forever. When an examiner needs to modify a feedback, ',
        '       they create a new feedback. Therefore, you see more than ',
        '       one feedback in the menu above. Unless there is something ',
        '       wrong with the latest feedback, you should not have to ',
        '       read this feedback',
        '   </div>',
        '</tpl>',
        '<div class="rendered_view">{rendered_view}<div>'
    ),

    constructor: function(config) {
        this.addEvents('afterStoreLoadMoreThanZero');
        return this.callParent([config]);
    },
    
    initComponent: function() {

        var me = this;
        this.staticfeedbackstore.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        this.staticfeedbackstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery',
            comp: 'exact',
            value: this.deliveryid
        }]);

        this.feedbackSelector = Ext.create('Ext.form.field.ComboBox', {
            store: this.staticfeedbackstore,
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

        Ext.apply(this, {
            tbar: [{
                xtype: 'box',
                flex: 1
            }, this.feedbackSelector]
        });
        this.callParent(arguments);
        this.loadStore();
    },

    loadStore: function() {
        var me = this;
        this.staticfeedbackstore.load({
            callback: function(records, operation, successful) {
                if(successful) {
                    if(records.length == 0) {
                        me.bodyWithNoFeedback();
                    }
                    else {
                        me.bodyWithFeedback(records);
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

    setBody: function(content) {
        this.removeAll();
        this.add(content);
    },

    setStaticFeedback: function(feedback) {
        var first = this.staticfeedbackstore.data.items[0].data.id;
        var tpldata = {isactive: first==feedback.id};
        Ext.apply(tpldata, feedback);
        this.setBody({
            xtype: 'component',
            cls: this.cls + '-feedbackview',
            html: this.tpl.apply(tpldata)
        });
    },

    bodyWithFeedback: function(records) {
        var first = records[0].data;
        this.feedbackSelector.setRawValue(first.save_timestamp);
        if(records.length > 1) {
            this.getToolbar().show();
            this.feedbackSelector.show();
        } else {
        }
        this.setStaticFeedback(first);
        this.fireEvent('afterStoreLoadMoreThanZero');
    },

    bodyWithNoFeedback: function() {
        me.getToolbar().hide();
        this.setBody({
            xtype: 'component',
            cls: 'no-feedback',
            html: 'No feedback yet'
        });
    },

    getToolbar: function() {
        return this.down('toolbar');
    }
});
