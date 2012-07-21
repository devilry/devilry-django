/**
 * A panel that displays information about multple groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'multiplegroupsview',
    ui: 'transparentpanel',
    requires: [
        'devilry_theme.Icons',
        'devilry_extjsextras.form.Help'
    ],

    /**
     * @cfg {string} topMessage (required)
     */

    /**
     * @cfg {string} multiselectHowto (required)
     */

    initComponent: function() {
        var buttonmargin = '20 0 0 0';
        var helpmargin = '4 0 0 0';
        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                //region: 'center',
                minHeight: 100,
                flex: 6,
                xtype: 'container',
                padding: '20 20 10 0',
                autoScroll: true,
                items: [{
                    xtype: 'alertmessage',
                    type: 'info',
                    message: [this.topMessage, this.multiselectHowto].join(' ')
                
                // Set examiners
                }, {
                    xtype: 'splitbutton',
                    margin: 0,
                    scale: 'medium',
                    text: gettext('Set examiner(s)'),
                    itemId: 'setExaminersButton',
                    menu: [{
                        text: gettext('Add examiner(s)'),
                        itemId: 'addExaminersButton',
                        tooltip: gettext('Add one or more examiner(s) to the selected groups.')
                    }, {
                        text: gettext('Clear examiners'),
                        itemId: 'clearExaminersButton',
                        icon: devilry_theme.Icons.DELETE_SMALL,
                        tooltip: gettext('Remove/clear all examiners from the selected groups.')
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: helpmargin,
                    html: gettext('Assign one or more examiner(s) to the selected groups. Use the arrow button for methods of setting examiners, such as random and by tags. Setting examiners <strong>replaces</strong> the current examiners.')

                // Set Tags
                }, {
                    xtype: 'splitbutton',
                    margin: buttonmargin,
                    scale: 'medium',
                    text: gettext('Set tag(s)'),
                    itemId: 'setTagsButton',
                    menu: [{
                        text: gettext('Add tag(s)'),
                        itemId: 'addTagsButton',
                        tooltip: gettext('Add one or more tag(s) to the selected groups.')
                    }, {
                        text: gettext('Clear tags'),
                        itemId: 'clearTagsButton',
                        icon: devilry_theme.Icons.DELETE_SMALL,
                        tooltip: gettext('Remove/clear all tags from the selected groups.')
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: helpmargin,
                    html: gettext('Assign one or more tag(s) to the selected groups. Use the arrow button for methods of setting tags, such as random and by tags. Setting tags <strong>replaces</strong> the current tags.')
                }]
            }, {
                flex: 4,
                minHeight: 150,
                xtype: 'selectedgroupssummarygrid'
            }]
        });
        this.callParent(arguments);
    }
});
