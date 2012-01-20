/** SearchWidget used in every page in the entire administrator interface.
 *
 * Enables users to search for everything (like the dashboard) or just within
 * the current item.
 * */
Ext.define('devilry.administrator.AdministratorSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.DashboardSearchWidget',

    nodeRowTpl: [
        '<div class="section popuplistitem">',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    subjectRowTpl: [
        '<div class="section popuplistitem">',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    periodRowTpl: [
        '<div class="section popuplistitem">',
        '    <p class="path">{parentnode__short_name}</p>',
        '    <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    /**
    * @cfg
    * Url prefix. Should be the absolute URL path to /administrator/.
    */
    urlPrefix: '',

    initComponent: function() {
        Ext.apply(this, {
            searchResultItems: [{
                xtype: 'searchresults',
                title: 'Nodes',
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedNode'),
                filterconfig: {
                    type: 'node'
                },
                resultitemConfig: {
                    tpl: this.nodeRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'node/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Subjects',
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedSubject'),
                filterconfig: {
                    type: 'subject'
                },
                resultitemConfig: {
                    tpl: this.subjectRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'subject/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Periods',
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedPeriod'),
                filterconfig: {
                    type: 'period'
                },
                resultitemConfig: {
                    tpl: this.periodRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'period/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignments',
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedAssignment'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignment,
                resultitemConfig: {
                    tpl: this.assignmentRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignment/{id}'
                    },
                    menuitems: [{
                        text: 'Show deliveries',
                        clickFilter: 'type:delivery assignment:{id}'
                    }]
                }
            }, {
                xtype: 'searchresults',
                title: 'Assignment groups',
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedAssignmentGroup'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.assignmentgroup,
                resultitemConfig: {
                    tpl: this.assignmentgroupRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{id}'
                    }
                }
            }, {
                xtype: 'searchresults',
                title: 'Deliveries',
                store: this._createStore('devilry.apps.administrator.simplified.SimplifiedDelivery'),
                filterconfig: devilry.extjshelpers.searchwidget.FilterConfigDefaults.delivery,
                resultitemConfig: {
                    tpl: this.deliveryRowTpl,
                    defaultbutton: {
                        text: 'View',
                        clickLinkTpl: this.urlPrefix + 'assignmentgroup/{deadline__assignment_group}?deliveryid={id}'
                    }
                }
            }]
        });
        this.callParent(arguments);
    },

    _createStore: function(modelname) {
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
        return store;
    }
});
