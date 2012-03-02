Ext.define('subjectadmin.view.createnewassignment.ChoosePeriod' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.chooseperiod',
    requires: [
        'themebase.layout.RightSidebar',
        'themebase.form.Help'
    ],

    layout: 'rightsidebar',

    items: [{
        xtype: 'container',
        region: 'main',
        items: [{
            xtype: 'container',
            cls: 'centerbox',
            items: [{
                xtype: 'box',
                html: Ext.String.format('<h2 class="centertitle">{0}</h2>', dtranslate('subjectadmin.chooseperiod.title')),
            }, {
                xtype: 'form',
                ui: 'transparentpanel',
                cls: 'centerbody',
                fieldDefaults: {
                    labelAlign: 'top',
                    labelStyle: 'font-weight: bold'
                },
                items: [{
                    margin: {top: 0, bottom: 20},
                    xtype: 'alertmessagelist'

                // Active period
                }, {
                    xtype: 'activeperiodslist',
                    name: 'activeperiod',
                    flex: 1,
                    fieldLabel: dtranslate('subjectadmin.assignment.activeperiod.label')
                }, {
                    xtype: 'formhelp',
                    margin: {top: 5},
                    html: dtranslate('subjectadmin.assignment.activeperiod.help')

                // How do students add deliveries
                }, {
                    flex: 1,
                    margin: {top: 20},
                    fieldLabel: dtranslate('subjectadmin.assignment.delivery_types.label'),
                    xtype: 'radiogroup',
                    vertical: true,
                    columns: 1,
                    items: [{
                        boxLabel: dtranslate('subjectadmin.assignment.delivery_types.electronic'),
                        name: 'delivery_types',
                        inputValue: 0,
                        checked: true
                    }, {
                        boxLabel: dtranslate('subjectadmin.assignment.delivery_types.nonelectronic'),
                        name: 'delivery_types',
                        inputValue: 1
                    }]
                }, {
                    xtype: 'formhelp',
                    margin: {top: 5},
                    html: dtranslate('subjectadmin.assignment.delivery_types.help')
                    
                }, {
                    xtype: 'nextbutton',
                    margin: {top: 10}
                }]
            }]
        }]
    }, {
        xtype: 'box',
        region: 'sidebar',
        html: dtranslate('subjectadmin.chooseperiod.sidebarhelp')
    }]
});
