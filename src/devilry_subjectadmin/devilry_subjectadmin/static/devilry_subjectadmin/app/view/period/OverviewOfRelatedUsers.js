/**
 * Overview of relatated users on a period.
 */
Ext.define('devilry_subjectadmin.view.period.OverviewOfRelatedUsers' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.overviewofrelatedusers',
    cls: 'devilry_subjectadmin_overviewofrelatedusers',
    requires: [
    ],

    listTemplate: [
        '<h2>{title}</h2>',
        '<ul class="relateduserlist relateduserlist_{type}">',
        '<tpl if="users !== undefined">',
            '<tpl if="users.length == 0">',
                '<em>', gettext('None'), '</em>',
            '</tpl>',
            '<tpl if="users.length &gt; 0">',
                '<tpl for="users">',
                    '<li relateduserlistitem relateduserlistitem_{user.username}>',
                        '{user.full_name}',
                    '</li>',
                '</tpl>',
            '</tpl>',
        '</tpl>',
        '<tpl if="loading">',
            gettext('Loading ...'),
        '</tpl>',
        '</ul>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            //frame: false,
            //border: 0,
            //bodyPadding: 40,
            autoScroll: true,
            layout: 'column',

            items: [{
                columnWidth: 0.5,
                xtype: 'box',
                tpl: '{msg}',
                data: {
                    msg: 'Help coming here'
                }
            }, {
                xtype: 'box',
                columnWidth: .25,
                itemId: 'students',
                tpl: this.listTemplate,
                data: this._getStudentTplData({
                    loading: true
                })
            }, {
                xtype: 'box',
                columnWidth: .25,
                itemId: 'examiners',
                tpl: this.listTemplate,
                data: this._getExaminerTplData({
                    loading: true
                })
            }]
        });
        this.callParent(arguments);
    },

    _getStudentTplData: function(extra) {
        var data = {
            type: 'students',
            title: gettext('Students')
        };
        Ext.apply(data, extra);
        return data;
    },

    _getExaminerTplData: function(extra) {
        var data = {
            type: 'examiners',
            title: gettext('Examiners')
        };
        Ext.apply(data, extra);
        return data;
    },

    setRelatedStudents: function() {

    }
});
