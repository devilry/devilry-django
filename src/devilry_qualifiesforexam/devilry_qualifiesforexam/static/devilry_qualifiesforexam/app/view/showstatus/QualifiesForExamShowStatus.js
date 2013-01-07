Ext.define('devilry_qualifiesforexam.view.showstatus.QualifiesForExamShowStatus' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.showstatus',
    cls: 'devilry_qualifiesforexam_preview',


    /**
     * @cfg {int} [periodid]
     */

    requires: [
        'devilry_qualifiesforexam.view.showstatus.ShowDetailsGrid',
        'devilry_extjsextras.PrimaryButton'
    ],


    summaryTpl: [
        '<h1 style="margin: 0 0 10px 0;">',
            gettext('Qualfied for final exam'),
        '</h1>',
        '<p>',
            gettext('TODO'),
        '</p>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            autoScroll: true,
            layout: 'anchor',
            padding: '40 40 0 40',
            items: [{
                xtype: 'container',
                cls: 'devilry_focuscontainer bootstrap',
                padding: 20,
                margin: '0 0 20 0',
                anchor: '100%',
                layout: 'fit',
                items: [{
                    xtype: 'panel',
                    itemId: 'summary',
                    tpl: this.summaryTpl,
                    autoScroll: true,
                    border: false,
                    data: {}
                }]
            }, {
                xtype: 'statusdetailsgrid',
                anchor: '100%',
                height: 300, // Initial height before it is autoset
                autoHeightMargin: 100
            }, {
                xtype: 'box',
                height: 40 // NOTE: get a "margin" below the table - padding does not seem to be respected
            }]
        });
        this.callParent(arguments);
    }
});
