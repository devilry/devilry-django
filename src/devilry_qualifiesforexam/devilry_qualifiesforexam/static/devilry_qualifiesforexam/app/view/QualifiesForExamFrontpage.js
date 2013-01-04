Ext.define('devilry_qualifiesforexam.view.QualifiesForExamFrontpage' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.frontpage',
    cls: 'devilry_qualifiesforexam_frontpage',

    requires: [
    ],

    padding: '40',
    layout: 'anchor',
    autoScroll: true,

    items: [{
        xtype: 'container',
        cls: 'devilry_focuscontainer',
        padding: '20',
        items: [{
            xtype: 'box',
            cls: 'bootstrap',
            html: [
                '<h1>',
                    gettext('Qualifies for final exams'),
                '</h1>',
                '<p>',
                    'TODO',
                '</p>'
            ].join('')
        }]
    }]
});
