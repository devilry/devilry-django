Ext.define('devilry_qualifiesforexam.view.selectplugin.QualifiesForExamSelectPlugin' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.selectplugin',
    cls: 'devilry_qualifiesforexam_selectplugin',

    /**
     * @cfg {int} [periodid]
     */

    requires: [
        'devilry_qualifiesforexam.view.selectplugin.ListPlugins'
    ],

    padding: '40',
    layout: 'anchor',
    autoScroll: true,

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                xtype: 'container',
                layout: 'anchor',
                anchor: '100%',
                cls: 'devilry_focuscontainer bootstrap',
                padding: '20',
                items: [{
                    xtype: 'box',
                    anchor: '100%',
                    html: [
                        '<h1>',
                            gettext('How do students qualify for final exams?'),
                        '</h1>'
                    ].join('')
                }, {
                    xtype: 'container',
                    layout: 'column',
                    items: [{
                        xtype: 'box',
                        width: 200,
                        html: [
                            '<p class="muted"><small>',
                              gettext('Select one of the options from the list. Each option starts a wizard that ends with a preview of the results before you get the option to save.'),
                            '</small></p>'
                        ].join('')
                    }, {
                        xtype: 'listplugins',
                        margin: '0 0 0 40',
                        columnWidth: '1',
                        periodid: this.periodid
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
