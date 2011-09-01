/** SearchWidget used in every page in the entire student interface.
 *
 * Enables users to search for everything (like the dashboard) or just within
 * the current item.
 * */
Ext.define('devilry.student.StudentSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],

    config: {
        /**
         * @cfg
         * Url prefix. Should be the absolute URL path to /student/.
         */
        urlPrefix: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for AssignmentGroup rows.
         */
        assignmentgroupRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Deadline rows.
         */
        deadlineRowTpl: '',

        /**
         * @cfg
         * ``Ext.XTemplate`` for Delivery rows.
         */
        deliveryRowTpl: ''
    },

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: 'Delivery',
                store: Ext.data.StoreManager.lookup('devilry.apps.student.simplified.SimplifiedDeliveryStoreSearch'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                itemtpldata: {
                    is_student: true
                },
                resultitemConfig: {
                    tpl: this.deliveryRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Open deadlines',
                store: Ext.data.StoreManager.lookup('devilry.apps.student.simplified.SimplifiedDeadlineStoreSearch'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.deadline,
                itemtpldata: {
                    is_student: true
                },
                alwaysAppliedFilters: [{
                    field: 'assignment_group__is_open',
                    comp: 'exact',
                    value: true
                }],
                resultitemConfig: {
                    tpl: this.deadlineRowTpl,
                    defaultbutton: {
                        text: 'Deliver',
                        clickLinkTpl: this.urlPrefix + 'add-delivery/{assignment_group}'
                    }
                }
            //}, {
                //xtype: 'searchresults',
                //title: 'My groups',
                //store: Ext.data.StoreManager.lookup('devilry.apps.student.simplified.SimplifiedAssignmentGroupStoreSearch'),
                //filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                //itemtpldata: {
                    //is_student: true
                //},
                //resultitemConfig: {
                    //tpl: this.assignmentgroupRowTpl,
                    //defaultbutton: {
                        //text: 'View',
                        //clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    //}
                //}
            }]
        });
        this.callParent(arguments);
    }
});
