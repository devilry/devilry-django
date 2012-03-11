/**
 * A panel that displays information about a single group.
 */
Ext.define('subjectadmin.view.managestudents.SingleGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'singlegroupview',
    ui: 'transparentpanel',

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */

    /**
     * @cfg {subjectadmin.model.Group} groupRecord (required)
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
                    dtranslate('themebase.not_finished_correcting'),
                '</span></tpl>',
            '</dd>',
            '<dt>', Ext.String.capitalize(dtranslate('themebase.deliveries')) ,':</dt> ',
            '<dd>{num_deliveries}</dd>',
        '</dl>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'alertmessage',
                type: 'info',
                message: [this.topMessage, this.multiselectHowto].join(' ')
            }, {
                xtype: 'container',
                layout: 'column',
                items: [{
                    xtype: 'container',
                    columnWidth: .7,
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: this._getMetaInfo()
                    }]
                }, {
                    xtype: 'container',
                    columnWidth: .3,
                    items: [{
                        xtype: 'panel',
                        title: 'Students',
                        html: 'body'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getMetaInfo: function() {
        var tpl = Ext.create('Ext.XTemplate', this.metaInfoTpl);
        var data = Ext.apply({
            passing_grade_i18n: dtranslate('themebase.passing_grade'),
            not_passing_grade_i18n: dtranslate('themebase.not_passing_grade'),
            points_i18n: dtranslate('themebase.points')
        }, this.groupRecord.data);
        return tpl.apply(data);
    }
});
