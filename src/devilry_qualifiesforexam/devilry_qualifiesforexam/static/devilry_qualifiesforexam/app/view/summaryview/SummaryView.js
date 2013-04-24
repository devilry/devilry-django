Ext.define('devilry_qualifiesforexam.view.summaryview.SummaryView' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.summaryview',
    cls: 'devilry_qualifiesforexam_summaryview',

    /**
     * @cfg {int} [nodeid]
     */

    requires: [
        'devilry_qualifiesforexam.view.summaryview.SummaryViewGrid'
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
                layout: 'fit',
                anchor: '100%',
                items: [{
                    xtype: 'box',
                    html: [
                        '<h1>', gettext('Qualified for exams summary'), '</h1>',
                        '<p class="muted">',
                            'TODO: Explain statuses',
                        '</p>'
                    ].join('')
                }]
            }, {
                xtype: 'summaryviewgrid',
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
