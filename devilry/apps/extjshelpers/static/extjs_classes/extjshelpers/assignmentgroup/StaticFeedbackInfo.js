/** Panel to show StaticFeedback info.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo', {
    extend: 'Ext.container.Container',
    alias: 'widget.staticfeedbackinfo',
    cls: 'widget-staticfeedbackinfo',
    requires: [
        'devilry.extjshelpers.Pager',
        'devilry.extjshelpers.SingleRecordContainer',
        'devilry.extjshelpers.assignmentgroup.FileMetaBrowserPanel',
        'devilry.extjshelpers.assignmentgroup.StaticFeedbackView',
        'devilry.extjshelpers.SingleRecordContainerDepButton',
        'devilry_extjsextras.DatetimeHelpers'
    ],

    assignmentgroup_recordcontainer: undefined,

    /**
     * @cfg {Ext.data.Store} [filemetastore]
     * FileMeta ``Ext.data.Store``. (Required).
     * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
     * class.
     */
    filemetastore: undefined,

    /**
     * @cfg {object} [staticfeedbackstore]
     * FileMeta ``Ext.data.Store``. (Required).
     * _Note_ that ``filemetastore.proxy.extraParams`` is changed by this
     * class.
     */
    staticfeedbackstore: undefined,

    /**
     * @cfg {object} [delivery_recordcontainer]
     * A {@link devilry.extjshelpers.SingleRecordContainer} for Delivery.
     */
    delivery_recordcontainer: undefined,

    titleTpl: [
        '<tpl if="loading">',
            gettext('Loading'), ' ...',
        '<tpl else>',
            '<h2 style="margin: 0 0 5 0;">',
                gettext('Delivery'), ' #{delivery.number}',
            '</h2>',
            '<p>',
                '<tpl if="assignmentgroup.parentnode__delivery_types === 1">',
                    '<span class="label label-info">',
                        gettext('Non-electronic delivery'),
                    '</span>',
                '<tpl else>',
                    gettext('Time of delivery: '),
                    '{[this.formatDatetime(values.delivery.time_of_delivery)]}',
                '</tpl>',
            '</p>',
        '</tpl>', {
            formatDatetime:function (dt) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
            }
        }
    ],


    constructor: function(config) {
        this.addEvents('afterStoreLoadMoreThanZero');
        this.callParent([config]);
        this.initConfig(config);
    },
    
    initComponent: function() {
        this.staticfeedback_recordcontainer = Ext.create('devilry.extjshelpers.SingleRecordContainer');
        this.bodyContent = Ext.create('Ext.container.Container', {
            layout: 'fit',
            autoScroll: true
        });

        var group = this.assignmentgroup_recordcontainer.record;
        Ext.apply(this, {
            layout: 'anchor',
            border: false,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'panel',
                border: false,
                cls: 'bootstrap',
                itemId: 'deliveryTitle',
                bodyStyle: 'background-color: transparent;',
                tpl: this.titleTpl,
                data: {
                    loading: true
                }
            }, {
                xtype: 'filemetabrowserpanel',
                store: this.filemetastore,
                hidden: true
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                itemId: 'isClosedMessage',
                hidden: group.get('is_open'),
                html: [
                    '<p class="alert alert-info">',
                        gettext('This group is closed. Students can not add deliveries on closed groups. Use the button above to re-open it if you need to change their feedback.'),
                    '</p>'
                ].join('')
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                html: [
                    '<h3 style="margin: 20px 0 0 0;">',
                        gettext('Feedback'),
                    '</h3>'
                ].join('')
            }, {
                xtype: 'panel',
                tbar: this.getToolbarItems(),
                layout: 'fit',
                margin: '0 0 20 0',
                items: this.bodyContent
            }]
        });
        this.callParent(arguments);

        this.staticfeedbackstore.pageSize = 1;
        this.staticfeedbackstore.proxy.extraParams.orderby = Ext.JSON.encode(['-save_timestamp']);

        this.staticfeedback_recordcontainer.addListener('setRecord', this.onSetStaticFeedbackRecord, this);
        this.staticfeedbackstore.addListener('load', this.onLoadStaticfeedbackstore, this);

        if(this.delivery_recordcontainer.record) {
            this.onLoadDelivery();
        }
        this.delivery_recordcontainer.addListener('setRecord', this.onLoadDelivery, this);
    },

    getToolbarItems: function() {
        var items = ['->', {
            xtype: 'devilrypager',
            store: this.staticfeedbackstore,
            width: 200,
            reverseDirection: true,
            middleLabelTpl: Ext.create('Ext.XTemplate',
                '<tpl if="firstRecord">',
                    '{currentNegativePageOffset})&nbsp;',
                    '{[this.formatDatetime(values.firstRecord.data.save_timestamp)]}',
                '</tpl>', {
                    formatDatetime:function (dt) {
                        return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(dt);
                    }
                }
            )
        }];
        return items;
    },


    onLoadDelivery: function() {
        this.staticfeedbackstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'delivery',
            comp: 'exact',
            value: this.delivery_recordcontainer.record.data.id
        }]);
        this.staticfeedbackstore.load();

        var deliveryrecord = this.delivery_recordcontainer.record;
        var staticfeedbackStore = deliveryrecord.staticfeedbacks();
        this.down('#deliveryTitle').update({
            loading: false,
            delivery: deliveryrecord.data,
            assignmentgroup: this.assignmentgroup_recordcontainer.record.data,
            feedback: staticfeedbackStore.count() > 0? staticfeedbackStore.data.items[0].data: undefined
        });
    },


    onSetStaticFeedbackRecord: function() {
        var isactive = this.staticfeedbackstore.currentPage === 1;
        this.setBody({
            xtype: 'staticfeedbackview',
            padding: 10,
            singlerecordontainer: this.staticfeedback_recordcontainer,
            extradata: {
                isactive: isactive
            }
        });
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    },

    onLoadStaticfeedbackstore: function(store, records, successful) {
        if(successful) {
            if(records.length === 0) {
                this.bodyWithNoFeedback();
            }
            else {
                this.staticfeedback_recordcontainer.setRecord(records[0]);
                this.fireEvent('afterStoreLoadMoreThanZero');
            }
       } else {
            // TODO: handle failure
        }
    },

    setBody: function(content) {
        this.bodyContent.removeAll();
        this.bodyContent.add(content);
    },


    bodyWithNoFeedback: function() {
        this.setBody({
            xtype: 'box',
            padding: 10,
            cls: 'no-feedback',
            html: 'No feedback'
        });
    }
});
