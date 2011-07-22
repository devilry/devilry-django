/** Panel to show StaticFeedback info.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.staticfeedbackinfo',
    cls: 'widget-staticfeedbackinfo',
    title: 'Feedback',
    requires: [
        'devilry.extjshelpers.Pager'
    ],

    config: {
        /**
         * @cfg
         * Delivery id. (Required).
         */
        deliveryid: undefined,

        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
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
        this.staticfeedbackstore.pageSize = 1;
        this.staticfeedbackstore.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);
        this.staticfeedbackstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery',
            comp: 'exact',
            value: this.deliveryid
        }]);

        Ext.apply(this, {
            tbar: [{
                xtype: 'devilrypager',
                store: this.staticfeedbackstore,
                width: 200,
                reverseDirection: true,
                middleLabelTpl: Ext.create('Ext.XTemplate',
                    '<tpl if="firstRecord">',
                    '   {currentNegativePageOffset})&nbsp;&nbsp;',
                    '   {firstRecord.data.save_timestamp:date}',
                    '</tpl>'
                )
            }, '->']
        });
        this.callParent(arguments);

        this.staticfeedbackstore.addListener('load', function(store, records, successful) {
            if(successful) {
                if(records.length == 0) {
                    me.bodyWithNoFeedback();
                }
                else {
                    me.bodyWithFeedback(records[0]);
                }
            } else {
                // TODO: handle failure
            }
        });
        this.loadFeedbackViewer();
    },

    loadFeedbackViewer: function() {
        this.getToolbar().show();
        this.staticfeedbackstore.load();
    },

    getHeader: function() {
        return this.dockedItems.items[0];
    },

    setBody: function(content) {
        this.removeAll();
        this.add(content);
    },

    setStaticFeedback: function(feedback) {
        var tpldata = {isactive: this.staticfeedbackstore.currentPage == 1};
        Ext.apply(tpldata, feedback);
        this.setBody({
            xtype: 'component',
            cls: this.cls + '-feedbackview',
            html: this.tpl.apply(tpldata)
        });
    },

    bodyWithFeedback: function(record) {
        this.setStaticFeedback(record.data);
        this.fireEvent('afterStoreLoadMoreThanZero');
    },

    bodyWithNoFeedback: function() {
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
