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
        itemId: 'loading',
        html: ['<p>', gettext('Loading') + ' ...', '</p>'].join('')
    }, {
        itemId: 'dashboard',
        tpl: [
            '<p>',
                gettext('Select an active {period_term} from the list at the top of the left side of this page.'),
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
