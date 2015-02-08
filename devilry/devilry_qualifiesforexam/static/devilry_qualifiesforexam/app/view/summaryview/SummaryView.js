Ext.define('devilry_qualifiesforexam.view.summaryview.SummaryView' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.summaryview',
    cls: 'devilry_qualifiesforexam_summaryview',

    /**
     * @cfg {int} [node_id]
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
                    tpl: [
                        '<h1>', gettext('Qualified for final exams summary'), '</h1>',
                        '<p>', gettext('Each course in the list below has one of the following statuses:'), '</p>',
                        '<dl>',
                            '<dt><span class="text-success">', gettext('Ready for export'), '</span></dt>',
                            '<dd>', gettext('The list of qualified students are ready for export. Use the view- or print-button to browse the list of qualified students.'), '</dd>',
                        '<dl>',
                        '<dl>',
                            '<dt><span class="muted">', gettext('None'), '</span></dt>',
                            '<dd>', gettext('The {subject} manager has not selected students that qualify for final exams yet.'), '</dd>',
                        '<dl>',
                        '<dl>',
                            '<dt><span class="text-warning">', gettext('Not ready for export (retracted)'), '</span></dt>',
                            '<dd>',
                                gettext('The course manager has retracted a previously "Ready for export" status. This may be bad if you have already exported the status.'),
                            '</dd>',
                        '<dl>',

                        '<p class="alert" style="margin-top: 10px;">',
                            '<strong class="text-warning">',
                                gettext('WARNING'),
                            '</strong>: ',
                            gettext('Devilry does NOT notify you when a status is changed. This could lead to problems when someone retracts or updates an exported status. Please contact the Devilry project if you want to help us create a good workflow for handling status changes.'),
                        '</p>'
                    ],
                    data: {}
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
