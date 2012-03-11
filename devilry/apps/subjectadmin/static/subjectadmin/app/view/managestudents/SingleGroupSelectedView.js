/**
 * A panel that displays information about a single group.
 */
Ext.define('subjectadmin.view.managestudents.SingleGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'singlegroupview',
    ui: 'transparentpanel',

    requires: [
        'subjectadmin.view.managestudents.StudentsInGroupGrid',
        'subjectadmin.view.managestudents.ExaminersInGroupGrid',
        'subjectadmin.view.managestudents.TagsInGroupGrid'
    ],

    /**
     * @cfg {string} multiselectHowto (required)
     */

    /**
     * @cfg {subjectadmin.model.Group} groupRecord (required)
     */

    /**
     * @cfg {Ext.data.Store} studentsStore (required)
     */

    /**
     * @cfg {Ext.data.Store} examinersStore (required)
     */

    /**
     * @cfg {Ext.data.Store} tagsStore (required)
     */

    metaInfoTpl: [
        '<dl>',
            '<dt>', dtranslate('themebase.grade') ,':</dt> ',
            '<dd>',
                '<tpl if="hasFeedback">',
                    '{feedback__grade} ',
                    '<tpl if="feedback__is_passing_grade"><span class="label label-success">',
                        dtranslate('themebase.passing_grade'),
                    '</span></tpl>',
                    '<tpl if="!feedback__is_passing_grade"><span class="label label-warning">',
                        dtranslate('themebase.not_passing_grade'),
                    '</span></tpl>',
                    ' <span class="label">',
                        dtranslate('themebase.points'), ': {feedback__points}',
                    '</span>',
                '</tpl>',
                '<tpl if="!hasFeedback"><span class="label label-info">',
                    dtranslate('themebase.no_feedback'),
                '</span></tpl>',
            '</dd>',

            '<dt>', Ext.String.capitalize(dtranslate('themebase.deliveries')) ,':</dt> ',
            '<dd>{num_deliveries}</dd>',

            '<dt>', dtranslate('themebase.status'), ':</dt>',
            '<dd>',
                '<tpl if="is_open">',
                    '<span class="label label-success">', dtranslate('themebase.open'), '</span> ',
                    dtranslate('themebase.open.explained'),
                '</tpl>',
                '<tpl if="!is_open">',
                    '<span class="label label-warning">', dtranslate('themebase.closed'), '</span> ',
                    dtranslate('themebase.closed.explained'),
                '</tpl>',
                ' ', dtranslate('subjectadmin.managestudents.open_close_explained_extra'),
            '</dd>',
        '</dl>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'alertmessage',
                type: 'info',
                message: this.multiselectHowto
            }, {
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'container',
                    columnWidth: .63,
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: this._getMetaInfo()
                    }]
                }, {
                    xtype: 'container',
                    columnWidth: .37,
                    padding: {left: 20},
                    defaults: {
                        margin: {top: 20}
                    },
                    items: [{
                        xtype: 'studentsingroupgrid',
                        margin: {top: 0},
                        store: this.studentsStore
                    }, {
                        xtype: 'examinersingroupgrid',
                        store: this.examinersStore
                    }, {
                        xtype: 'tagsingroupgrid',
                        store: this.tagsStore
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getMetaInfo: function() {
        var tpl = Ext.create('Ext.XTemplate', this.metaInfoTpl);
        var data = Ext.apply({
            hasFeedback: this.groupRecord.get('feedback__save_timestamp') != null,
            passing_grade_i18n: dtranslate('themebase.passing_grade'),
            not_passing_grade_i18n: dtranslate('themebase.not_passing_grade'),
            points_i18n: dtranslate('themebase.points')
        }, this.groupRecord.data);
        return tpl.apply(data);
    }
});
