Ext.define('devilry_subjectadmin.view.createnewperiod.CreateNewPeriod', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.createnewperiod',
    cls: 'devilry_createnewperiod',
    requires: [
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.PrimaryButton',
        'devilry_subjectadmin.utils.BaseNodeHelp'
    ],


    /**
     * @cfg {String} subject_id (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            frame: false,
            border: false,
            bodyPadding: '20 40 20 40',
            autoScroll: true,
            oktext: gettext('Create'),
            layout: 'anchor',

            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                margin: '0 0 20 0',
                itemId: 'header',
                tpl: '<h1>{heading} <small>- {subheading}</small></h1>',
                data: {
                    heading: gettext('Loading') + ' ...',
                    subheading: ''
                }
            }, {
                xtype: 'alertmessagelist',
                itemId: 'formErrorList',
                padding: '0 0 20 0'
            }, {
                xtype: 'form',
                bodyPadding: 20,
                fieldDefaults: {
                    labelAlign: 'top',
                    labelStyle: 'font-weight: bold'
                },
                defaults: {
                    margin: '10 0 0 0'
                },
                items: [{
                    xtype: 'container',
                    margin: '0 0 0 0',
                    layout: 'column',
                    items: [{
                        columnWidth: 1,
                        name: "long_name",
                        fieldLabel: gettext('Long name'),
                        xtype: 'textfield',
                        cls: 'largefont',
                        emptyText: pgettext('createnewassignment', 'Example: Spring 1970'),
                        allowBlank: false,
                        padding: '0 20 0 0'
                    }, {
                        name: "short_name",
                        width: 200,
                        fieldLabel: gettext('Short name'),
                        xtype: 'textfield',
                        allowBlank: false,
                        emptyText: pgettext('createnewassignment', 'Example: spring1970')
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: '5 0 0 0',
                    html: devilry_subjectadmin.utils.BaseNodeHelp.getShortAndLongNameHelp()
                }, {

                    xtype: 'devilry_extjsextras-datetimefield',
                    fieldLabel: gettext('Start time'),
                    width: 300,
                    itemId: 'new_period_start_time',
                    cls: 'start_time_field',
                    allowBlank: false,
                    name: 'start_time'
                }, {
                    xtype: 'devilry_extjsextras-datetimefield',
                    fieldLabel: gettext('End time'),
                    width: 300,
                    allowBlank: false,
                    id: 'new_period_end_time',
                    cls: 'end_time_field',
                    name: 'end_time'
                }],
                buttons: [{
                    xtype: 'primarybutton',
                    formBind: true,
                    itemId: 'saveButton',
                    text: gettext('Create')
                }]
            }]
        });
        this.callParent(arguments);
    }
});
