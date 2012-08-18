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
                title: gettext('Deliveries'),
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedDelivery'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: this.deliveryRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Groups'),
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedAssignmentGroup'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    },
                    menuitems: [{
                        text: interpolate('Show %(deliveries_term)s', {
                            deliveries_term: gettext('deliveries')
                        }, true),
                        clickFilter: 'type:delivery group:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: gettext('Assignments'),
                store: this._createStore('devilry.apps.examiner.simplified.SimplifiedAssignment'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: this.assignmentRowTpl,
                    defaultbutton: {
                        text: gettext('View'),
                        clickLinkTpl: this.urlPrefix + 'assignment/{id}'
                    },
                    menuitems: [{
                        text: interpolate(gettext('Show %(groups_term)s'), {
                            groups_term: gettext('groups')
                        }, true),
                        clickFilter: 'type:group assignment:{id}'
                    }, {
                        text: interpolate('Show %(deliveries_term)s', {
                            deliveries_term: gettext('deliveries')
                        }, true),
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }]
        });
        this.callParent(arguments);
    }
});
