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
            items: [{
                xtype: 'alertmessage',
                type: 'info',
                message: [this.topMessage, this.multiselectHowto].join(' ')
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                html: '<strong>NOTE:</strong> This view is incomplete. Please see <a href="http://heim.ifi.uio.no/espeak/devilry-figures/managestudents-multiselect.png" target="_blank">this image mockup</a> of the planned interface.'
            }, {
                xtype: 'splitbutton',
                margin: buttonmargin,
                scale: 'medium',
                text: gettext('Set examiners'),
                itemId: 'setExaminersButton',
                menu: [{
                    text: 'TODO'
                }]
            }, {
                xtype: 'formhelp',
                margin: helpmargin,
                html: gettext('Assign one or more examiner(s) to the selected groups. Use the arrow button for methods of setting examiners, such as random and by tags. Setting examiners <strong>replaces</strong> the current examiners.')
            }]
        });
        this.callParent(arguments);
    }
});
