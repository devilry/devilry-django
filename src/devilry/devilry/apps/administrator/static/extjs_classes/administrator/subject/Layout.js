Ext.define('devilry.administrator.subject.Layout', {
    extend: 'Ext.container.Container',
    alias: 'widget.administrator-subjectlayout',

    requires: [
        'devilry.administrator.subject.PrettyView',
        'devilry.extjshelpers.RestfulSimplifiedEditPanel',
        'devilry.extjshelpers.forms.administrator.Subject',
        'devilry.administrator.ListOfChildnodes'
    ],
    
    /**
     * @cfg
     */
    subjectid: undefined,

    subjectmodel_name: 'devilry.apps.administrator.simplified.SimplifiedSubject',
    
    initComponent: function() {
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.heading = Ext.ComponentManager.create({
                xtype: 'component',
                data: {},
                cls: 'section pathheading',
                tpl: [
                    '<tpl if="!hasdata">',
                        '<span class="loading">Loading...</span>',
                    '</tpl>',
                    '<tpl if="hasdata">',
                        '<h1>{subject.long_name}</h1>',
                    '</tpl>'
                ]
            }), {
                xtype: 'tabpanel',
                flex: 1,
                items: [{
                    xtype: 'administrator-listofchildnodes',
                    title: 'Periods/semesters',
                    parentnodeid: this.subjectid,
                    orderby: 'start_time',
                    modelname: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
                    readable_type: 'period/semester',
                    urlrolepart: 'period'
                }, this.prettyview = Ext.widget('administrator_subjectprettyview', {
                    title: 'Administer',
                    modelname: this.subjectmodel_name,
                    objectid: this.subjectid,
                    dashboardUrl: DASHBOARD_URL,
                    listeners: {
                        scope: this,
                        loadmodel: this._onLoadRecord,
                        loadmodelFailed: this._onLoadRecordFailed,
                        edit: this._onEdit
                    }
                })]
            }]
        });
        this.callParent(arguments);
    },

    _onLoadRecord: function(subjectRecord) {
        this.heading.update({
            hasdata: true,
            subject: subjectRecord.data
        });
        this._setBreadcrumbAndTitle(subjectRecord);
    },

    _onLoadRecordFailed: function(operation) {
        this.removeAll();
        var title = operation.error.statusText;
        if(operation.error.status == '403') {
            title = gettext('Permission denied');
            message = gettext('You are not administrator on this item or any of its parents.');
        }
        this.add({
            xtype: 'box',
            padding: 20,
            tpl: [
                '<div class="section warning">',
                    '<h2>{title}</h2>',
                    '<p>{message}</p>',
                '</div>'
            ],
            data: {
                title: title,
                message: message
            }
        });
    },

    _setBreadcrumbAndTitle: function(subjectRecord) {
        window.document.title = Ext.String.format('{0} - Devilry', subjectRecord.get('short_name'));
        devilry_header.Breadcrumbs.getInBody().set([], subjectRecord.get('short_name'));
    },

    _onEdit: function(record, button) {
        var editpanel = Ext.ComponentManager.create({
            xtype: 'restfulsimplified_editpanel',
            model: this.subjectmodel_name,
            editform: Ext.widget('administrator_subjectform'),
            record: record
        });
        var editwindow = Ext.create('devilry.administrator.DefaultEditWindow', {
            editpanel: editpanel,
            prettyview: this.prettyview
        });
        editwindow.show();
    }
});
