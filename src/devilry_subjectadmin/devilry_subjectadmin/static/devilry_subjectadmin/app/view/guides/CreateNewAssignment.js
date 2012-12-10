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
                gettext('Select an active {subject_term} from the list at the top of the left side of this page.'),
            '</p>',
            '<p><small>',
                gettext('For {subjects_term} where you only have admin rights for selected assignments, those assignments will be listed. If you only have assignments in your list, you do not have the required rights to create new assignments.'),
            '</small></p>'
        ],
        data: {
            subject_term: gettext('subject'),
            subjects_term: gettext('subjects')
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
                gettext('Keeping the defaults is usually the best choice if you are uncertain.'),
            '</p>',

            '<h3>', gettext('Need to edit students or examiners?'), '</h3>',
            '<p>',
                gettext('The links to view or edit students and examiners open a new browser window, so you will not loose your progress when you click them.'),
            '</p>',

            '<h3>', gettext('Create another?'), '</h3>',
            '<p>',
                gettext('This guide closes when you click Create new assignment. At the top of the next page, you will get a link to quickly create another assignment with the same settings that you used for this assignment.'),
            '</p>'
        ],
        data: {
            subject_term: gettext('subject')
        }
    }]
});
