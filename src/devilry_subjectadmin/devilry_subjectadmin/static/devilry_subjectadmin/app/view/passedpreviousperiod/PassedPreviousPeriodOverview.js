Ext.define('devilry_subjectadmin.view.passedpreviousperiod.PassedPreviousPeriodOverview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.passedpreviousperiodoverview',
    cls: 'devilry_subjectadmin_passedpreviousperiodoverview',
    requires: [
        'devilry_subjectadmin.view.passedpreviousperiod.SelectGroupsGrid',
        'devilry_subjectadmin.view.passedpreviousperiod.ConfirmGroupsGrid',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.AlertMessage'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            bodyPadding: '20 40 20 40',
            layout: 'border',
            border: false,

            items: [{
                xtype: 'box',
                region: 'north',
                height: 70,
                cls: 'bootstrap',
                html: [
                    '<h1>',
                        gettext('Passed previously'),
                    '</h1>'
                    ].join('')
            }, {
                xtype: 'container',
                region: 'center',
                layout: 'card',
                itemId: 'cardContainer',
                items: [{
                    xtype: 'container',
                    itemId: 'pageOne',
                    layout: 'border',
                    items: [{
                        xtype: 'selectpassedpreviousgroupsgrid',
                        region: 'center',

                        fbar: [{
                            xtype: 'checkbox',
                            boxLabel: gettext('Show groups that Devilry believes should not be marked as previously passed?'),
                            itemId: 'showUnRecommendedCheckbox',
                            cls: 'showUnRecommendedCheckbox'
                        }, '->', {
                            xtype: 'button',
                            scale: 'large',
                            text: gettext('Next'),
                            disabled: true,
                            itemId: 'nextButton'
                        }]
                    }, {
                        xtype: 'box',
                        region: 'east',
                        width: 300,
                        cls: 'bootstrap',
                        padding: '0 0 0 30',
                        html: [
                            '<p class="muted">',
                                gettext('Select one or more groups. Groups that we belive have passed this assignment before has been selected automatically, and they are marked with the name of the old assignment.'),
                            '</p>',
                            '<p class="muted"><small>',
                                gettext('The search for previously passed students match the short name of old assignments against the short name of this assignment. Only groups with exactly one student in both the old and the current assignment is matched.'),
                            '</small></p>'
                        ].join('')
                    }]
                }, {
                    xtype: 'container',
                    itemId: 'pageTwo',
                    layout: 'border',
                    items: [{
                        xtype: 'box',
                        region: 'east',
                        width: 300,
                        cls: 'bootstrap',
                        padding: '0 0 0 30',
                        html: [
                            '<p class="muted">',
                                gettext('Make sure you really want to mark these groups as previously passed before saving.'),
                            '</p>',
                            '<p class="muted"><small>',
                                gettext('This will create a new delivery on each of the groups, mark the delivery as a placeholder for a previously approved delivery, and create a feedback with passing grade on the delivery.'),
                            '</small></p>'
                        ].join('')
                    }, {
                        xtype: 'confirmpassedpreviousgroupsgrid',
                        region: 'center',
                        fbar: [{
                            xtype: 'button',
                            text: gettext('Back'),
                            itemId: 'backButton'
                        }, '->', {
                            xtype: 'primarybutton',
                            text: gettext('Save'),
                            itemId: 'saveButton'
                        }]
                    }]
                }, {
                    itemId: 'unsupportedGradeEditor',
                    xtype: 'alertmessage',
                    type: 'error',
                    title: 'Unsupported grading system',
                    message: 'The passed previously functionality only supports the <em>Approved/not approved</em> grading system. We will fix this before the version you are testing is released.'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
