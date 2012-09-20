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
    }, {
        itemId: 'createnewassignment1',
        tpl: [
            '<p>',
                gettext('Fill out the visible fields in the form.'),
            '</p>',

            '<h3>', gettext('Exam?'), '</h3>',
            '<p>',
                gettext('Click Advanced, and choose Anonymous.'),
            '</p>',

            '<h3>', gettext('Paper deliveries?'), '</h3>',
            '<p>',
                gettext('If your students hand in deliveries on paper, choose Not using Devilry.'),
            '</p>'
        ],
        data: {
        }
    }, {
        itemId: 'createnewassignment2',
        tpl: [
            '<p>',
                gettext('Keep the defaults, or make sure you understand the consequence of unchecking the checkboxes.'),
            '</p>',
            '<p>',
                gettext('This guide closes when you click Create assignment.'),
            '</p>'
        ],
        data: {
        }
    }]
});
