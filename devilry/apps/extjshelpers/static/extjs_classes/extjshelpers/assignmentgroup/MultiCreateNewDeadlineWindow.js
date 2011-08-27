Ext.define('devilry.extjshelpers.assignmentgroup.MultiCreateNewDeadlineWindow', {
    extend: 'devilry.extjshelpers.RestfulSimplifiedEditWindowBase',
    alias: 'widget.multicreatenewdeadlinewindow',
    title: 'Create deadline',
    width: 700,
    height: 450,

    requires: [
        'devilry.extjshelpers.RestfulSimplifiedEditPanelBase',
        'devilry.extjshelpers.forms.Deadline'
    ],

    config: {

        /**
         * @cfg
         * Deadline ``Ext.data.Model``.
         */
        deadlinemodel: undefined
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {

        Ext.apply(this, {
            editpanel: Ext.widget('restfulsimplified_editpanel_base', {
                model: this.deadlinemodel,
                editform: Ext.create('devilry.extjshelpers.forms.Deadline')
            }),
        });
        this.callParent(arguments);
    }
});
