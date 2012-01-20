/** SearchWidget used in every page in the entire administrator interface.
 *
 * Enables users to search for everything (like the dashboard) or just within
 * the current item.
 * */
Ext.define('devilry.administrator.AdministratorSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],

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

    assignmentRowTpl: [
        '<div class="section popuplistitem">',
        '    <p class="path">',
        '{parentnode__parentnode__short_name}.',
        '{parentnode__short_name}',
        '   </p>',
        '   <h1>{long_name:ellipsis(40)}</h1>',
        '</div>'
    ],

    assignmentgroupRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{parentnode__parentnode__parentnode__short_name:ellipsis(60)}.',
        '{parentnode__parentnode__short_name:ellipsis(60)}.',
        '{parentnode__short_name:ellipsis(60)}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <h1><ul class="useridlist"><tpl for="candidates__identifier"><li>{.}</li></tpl></ul></h1>',
        '   </tpl>',
        '   <p><tpl if="name">{name}</tpl><p>',
        '</div>'
    ],

    deliveryRowTpl: [
        '<div class="section popuplistitem">',
        '   <p class="path">',
        '{deadline__assignment_group__parentnode__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__parentnode__short_name}.',
        '{deadline__assignment_group__parentnode__short_name}',
        '   </p>',
        '   <tpl if="!is_student">',
        '       <ul class="useridlist"><tpl for="deadline__assignment_group__candidates__identifier"><li>{.}</li></tpl></ul>',
        '   </tpl>',
        '   <tpl if="deadline__assignment_group__name"> &ndash; {deadline__assignment_group__name}</tpl>',
        '   <div class="section dl_valueimportant">',
        '      <div class="section">',
        '          <h1>Delivery number</h1>',
        '          {number}',
        '      </div>',
        '   </div>',
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
