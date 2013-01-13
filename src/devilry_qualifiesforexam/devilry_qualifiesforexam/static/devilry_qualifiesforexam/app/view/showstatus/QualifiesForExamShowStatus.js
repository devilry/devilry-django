Ext.define('devilry_qualifiesforexam.view.showstatus.QualifiesForExamShowStatus' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.showstatus',
    cls: 'devilry_qualifiesforexam_preview',


    /**
     * @cfg {int} [periodid]
     */

    requires: [
        'devilry_qualifiesforexam.view.showstatus.ShowDetailsGrid',
        'devilry_extjsextras.MarkupMoreInfoBox'
    ],


    summaryTpl: [
        '<h1 style="margin: 0 0 10px 0;">',
            gettext('Qualified for final exam'),
        '</h1>',
        '<tpl if="loading">',
            '<p class="muted">', gettext('Loading'), '...</p>',
        '<tpl else>',
            '<p class="status-numberedsummary">',
                '<span class="muted">', gettext('Status'), ':</span> ',
                '<span class="status-text label label-{[this.getClassForStatus(values.status)]}">',
                    '{statustext}',
                '</span>',
                ' <small class="muted createtime">(',
                    gettext('Saved {savetime} by {saveuser}'),
                ')</small>',
                '<br />',
                gettext('{qualifiedstudents}/{totalstudents} students qualifies for final exams.'),
                ' <small>{MORE_BUTTON}</small>',
            '</p>',
            '<div {MORE_ATTRS}>',
                '<div class="well well-small">',
                    '<dl style="margin-bottom: 0;">',
                        '<dt>', gettext('Plugin'), '</dt>',
                        '<dd>{plugin_title}</dd>',
                        '<tpl if="pluginsettings_summary">',
                            '<dt>', gettext('Settings'), '</dt>',
                            '<dd>{pluginsettings_summary}</dd>',
                        '</tpl>',
                        '<dt>', gettext('Details'), '</dt>',
                        '<dd>',
                            gettext('See the table below for details. The table includes detailed information about the results of each student for all assignments. This information may not match the information used to calculate if the students qualify for exams when students have been given new feedback after the status was saved.'),
                        '</dd>',
                    '</dl>',
                '</div>',
            '</div>',
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
                    border: false,
                    layout: 'fit',
                    data: {
                        loading: true
                    },
                    items: {
                        xtype: 'markupmoreinfobox',
                        itemId: 'summary',
                        tpl: this.summaryTpl
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
