/**
 * A panel that displays information about multple groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.MultipleGroupsSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.multiplegroupsview',
    cls: 'multiplegroupsview',
    ui: 'transparentpanel',
    requires: [
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
                }, {
                    xtype: 'splitbutton',
                    margin: buttonmargin,
                    scale: 'medium',
                    text: gettext('Set examiner(s)'),
                    itemId: 'setExaminersButton',
                    menu: [{
                        text: 'TODO'
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: helpmargin,
                    html: gettext('Assign one or more examiner(s) to the selected groups. Use the arrow button for methods of setting examiners, such as random and by tags. Setting examiners <strong>replaces</strong> the current examiners.')
                }, {
                    xtype: 'splitbutton',
                    margin: buttonmargin,
                    scale: 'medium',
                    text: gettext('Add examiner(s)'),
                    itemId: 'addExaminersButton',
                    menu: [{
                        text: 'TODO'
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: helpmargin,
                    html: gettext('Add one or more examiner(s) to the selected groups. Use the arrow button for more methods of adding examiners, such as random and by tags.')
                }, {
                    xtype: 'button',
                    margin: buttonmargin,
                    scale: 'medium',
                    text: gettext('Clear examiners'),
                    itemId: 'clearExaminersButton'
                }, {
                    xtype: 'formhelp',
                    margin: helpmargin,
                    html: gettext('Remove/clear all examiners from the selected groups.')
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
