/** SearchWidget used in every page in the entire examiner interface.
 * */
Ext.define('devilry.examiner.ExaminerSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.DashboardSearchWidget',

    /**
     * @cfg
     * Url prefix. Should be the absolute URL path to /student/.
     */
    urlPrefix: '',

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: 'Deliveries',
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedDelivery'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: this.deliveryRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignment groups',
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedAssignmentGroup'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: 'View/edit',
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    },
                    menuitems: [{
                        text: 'Show deliveries',
                        clickFilter: 'type:delivery group:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignments',
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedAssignment'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: this.assignmentRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignment/{id}'
                    },
                    menuitems: [{
                        text: 'Show groups',
                        clickFilter: 'type:group assignment:{id}'
                    }, {
                        text: 'Show deliveries',
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }]
        });
        this.callParent(arguments);
    }
});
