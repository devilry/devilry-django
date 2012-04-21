/** SearchWidget used in every page in the entire student interface.
 *
 * Enables users to search for everything (like the dashboard) or just within
 * the current item.
 * */
Ext.define('devilry.student.StudentSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.DashboardSearchWidget',

    /**
     * @cfg
     * Url prefix. Should be the absolute URL path to /student/.
     */
    urlPrefix: '',

    deadlineRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{assignment_group__parentnode__parentnode__parentnode__short_name}.',
        '{assignment_group__parentnode__parentnode__short_name}.',
        '{assignment_group__parentnode__short_name}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <ul class="useridlist"><tpl for="assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>',
        '   </tpl>',
        '   <h1>{deadline:date}</h1>',
        '   <p><tpl if="assignment_group__name"> &ndash; {assignment_group__name}</tpl><p>',
        '   <div class="section dl_valueimportant">',
        '       <div class="section">',
        '           <h1>Deliveries</h1>',
        '           {number_of_deliveries}',
        '       </div>',
        '   </div>',
        '</div>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: 'Deliveries',
                store: this._createStore('devilry.apps.student.simplified.SimplifiedDelivery'),
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
                store: this._createStore('devilry.apps.student.simplified.SimplifiedDeadline'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.deadline,
                itemtpldata: {
                    is_student: true
                },
                alwaysAppliedFilters: [{
                    field: 'assignment_group__is_open',
                    comp: 'exact',
                    value: true
                }, {
                    field: 'assignment_group__parentnode__delivery_types',
                    comp: 'exact',
                    value: 0 // Electronic deliveries
                }],
                resultitemConfig: {
                    tpl: this.deadlineRowTpl,
                    defaultbutton: {
                        text: 'Deliver',
                        clickLinkTpl: this.urlPrefix + 'add-delivery/{assignment_group}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignments',
                store: this._createStore('devilry.apps.student.simplified.SimplifiedAssignmentGroup'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                itemtpldata: {
                    is_student: true
                },
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    }
                }
            }]
        });
        this.callParent(arguments);
    }
});
