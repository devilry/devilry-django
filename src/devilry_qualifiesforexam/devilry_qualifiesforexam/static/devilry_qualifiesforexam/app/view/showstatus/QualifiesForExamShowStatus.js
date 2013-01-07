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
            layout: 'anchor',
            padding: '20',
            items: [{
                xtype: 'container',
                cls: 'devilry_focuscontainer bootstrap',
                padding: 20,
                height: 195,
                margin: '0 0 20 0',
                layout: 'fit',
                items: [{
                    xtype: 'panel',
                    itemId: 'summary',
                    tpl: this.summaryTpl,
                    autoScroll: true,
                    border: false,
                    data: {},
//                    fbar: [{
//                        xtype: 'button',
//                        itemId: 'backButton',
//                        text: gettext('Back')
//                    }, {
//                        xtype: 'primarybutton',
//                        itemId: 'saveButton',
//                        text: gettext('Save')
//                    }]
                }]
            }, {
                xtype: 'statusdetailsgrid',
                anchor: '0 -215'
            }]
        });
        this.callParent(arguments);
    }
});
