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
        '<tpl if="loading">',
            '<p class="muted">', gettext('Loading'), '...</p>',
        '<tpl else>',
            '<p class="muted status-numberedsummary">',
                gettext('{qualifiedstudents}/{totalstudents} students qualifies for final exams.'),
            '</p>',
            '<p>',
                '<span class="muted">', gettext('Status'), ':</span> ',
                '<span class="status-text label label-success">',
                    '{statustext}',
                '</span>',
            '</p>',
            '<tpl if="message">',
                '<h2>', gettext('Message'), '</h2>',
                '<p>{message}</p>',
            '</tpl>',
        '</tpl>'
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
                    data: {
                        loading: true
                    }
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
