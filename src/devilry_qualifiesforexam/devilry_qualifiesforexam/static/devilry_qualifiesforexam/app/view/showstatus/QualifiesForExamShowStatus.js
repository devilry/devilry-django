Ext.define('devilry_qualifiesforexam.view.showstatus.QualifiesForExamShowStatus' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.showstatus',
    cls: 'devilry_qualifiesforexam_preview',


    /**
     * @cfg {int} [periodid]
     */

    requires: [
        'devilry_qualifiesforexam.view.showstatus.ShowDetailsGrid'
    ],


    summaryTpl: [
        '<h1 style="margin: 0 0 10px 0;">',
            gettext('Qualified for final exam'),
        '</h1>',
        '<tpl if="loading">',
            '<p class="muted">', gettext('Loading'), '...</p>',
        '<tpl else>',
            '<p class="status-numberedsummary">',
                gettext('{qualifiedstudents}/{totalstudents} students qualifies for final exams.'),
                ' <small class="muted">',
                    gettext('See the table below for details. The table includes detailed information about the results of each student for all assignments. This information may not match the information used to calculate if the students qualify for exams if students have been given new feedback after the status was saved.'),
                '</small>',
            '</p>',
            '<p>',
                '<span class="muted">', gettext('Status'), ':</span> ',
                '<span class="status-text label label-{[this.getClassForStatus(values.status)]}">',
                    '{statustext}',
                '</span>',
                ' <small class="muted createtime">(',
                    gettext('Saved {savetime} by {saveuser}'),
                ')</small>',
            '</p>',
            '<tpl if="message">',
                '<div class="alert alert-info" style="white-space:pre-line;">',
                    '<strong>', gettext('Message') ,':<br/></strong>',
                    '{message}',
                '</div>',
            '</tpl>',
        '</tpl>', {
            getClassForStatus: function (status) {
                var map = {
                    ready: 'success',
                    almostready: 'info',
                    notready: 'warning'
                };
                return map[status];
            }
        }
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
                    },
                    dockedItems: {
                        xtype: 'toolbar',
                        dock: 'bottom',
                        ui: 'footer',
                        items: [{
                            xtype: 'button',
                            scale: 'medium',
                            text: gettext('Change status'),
                            menu: [{
                                text: gettext('Retract - change the status to "Not ready for export"'),
                                itemId: 'retractButton'
                            }, {
                                text: gettext('Update - re-run the qualified for final exams wizard'),
                                itemId: 'updateButton'
                            }]
                        }]
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
