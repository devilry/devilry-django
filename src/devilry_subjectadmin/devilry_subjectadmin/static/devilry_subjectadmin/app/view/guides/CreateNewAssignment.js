Ext.define('devilry_subjectadmin.view.guides.CreateNewAssignment', {
    extend: 'Ext.container.Container',
    alias: 'widget.guide-createnewassignment',

    /**
     * @cfg {devilry_subjectadmin.controller.GuideSystem} [guideSystem]
     */

    layout: 'card',
    defaults: {
        xtype: 'box'
    },
    items: [{
        itemId: 'dashboard',
        tpl: [
            '<p>',
                gettext('Select an active {period_term}.'),
            '</p>'
        ],
        data: {
            period_term: gettext('period')
        }
    }, {
        itemId: 'period',
        tpl: [
            '<p>',
                gettext('Click <em>Create new assignment</em>.'),
            '</p>'
        ],
        data: {
        }
    }]
});
