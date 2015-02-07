Ext.define('devilry_subjectadmin.view.createnewassignment.Form', {
    extend: 'Ext.form.Panel',
    alias: 'widget.createnewassignmentform',
    requires: [
        'Ext.form.field.ComboBox',
        'Ext.form.field.Text',
        'Ext.form.field.Hidden',
        'Ext.toolbar.Toolbar',
        'devilry_extjsextras.form.DateTimeField',
        'devilry_extjsextras.CreateButton',
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_subjectadmin.utils.BaseNodeHelp',
        'devilry_subjectadmin.view.createnewassignment.SelectSingleAssignment'
    ],

    /**
     * @cfg period_id
     */


    initComponent: function() {
        var cssclasses = 'devilry_subjectadmin_createnewassignmentform';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        var sideheading_attrs = 'class="muted" style="margin:0; padding:0; font-weight:normal; font-size:18px;"';
        var sideheading_width = 170;

        Ext.apply(this, {
            frame: false,
            bodyCls: 'devilry_focuscontainer',
            bodyPadding: 20,
            layout: 'anchor',
            fieldDefaults: {
                labelAlign: 'top',
                labelStyle: 'font-weight: bold'
            },
            items: [{
                xtype: 'container',
                layout: 'card',
                itemId: 'cardPanel',
                items: [{
                    xtype: 'panel',
                    itemId: 'pageOne',
                    cls: 'page1',
                    bodyPadding: '0 0 20 0',
                    border: false,
                    items: [{

                        // Long name
                        xtype: 'container',
                        layout: 'column',
                        items: [{
                            columnWidth: 1,
                            name: "long_name",
                            fieldLabel: gettext('Long name'),
                            xtype: 'textfield',
                            cls: 'hugefield',
                            emptyText: pgettext('createnewassignment', 'Example: Obligatory assignment one'),
                            allowBlank: false,
                            //fieldStyle: 'height:auto; font-size:20px; line-height:normal;',
                            padding: '0 20 0 0'
                        }, {
                            name: "short_name",
                            width: 300,
                            fieldLabel: gettext('Short name'),
                            xtype: 'textfield',
                            allowBlank: false,
                            emptyText: pgettext('createnewassignment', 'Example: oblig-1')
                        }]
                    }, {
                        xtype: 'box',
                        cls: 'bootstrap',
                        margin: '0 0 0 0',
                        html: [
                            '<p class="muted"><small>',
                                devilry_subjectadmin.utils.BaseNodeHelp.getShortAndLongNameHelp(),
                            '</small></p>'
                        ].join('')

                    }, {
                        xtype: 'container',
                        margin: '20 0 0 0',
                        layout: 'column',
                        items: [{
                            // How do students add deliveries
                            xtype: 'container',
                            columnWidth: 1,
                            padding: '0 40 20 0',
                            items: [{
                                xtype: 'radiogroup',
                                fieldLabel: gettext('How do students add deliveries?'),
                                vertical: true,
                                itemId: 'deliveryTypesRadioGroup',
                                cls: 'delivery_types-radiogroup',
                                columns: 1,
                                items: [{
                                    boxLabel: gettext('Using Devilry'),
                                    name: 'delivery_types',
                                    cls: 'deliveryTypesElectronic',
                                    inputValue: 0,
                                    checked: true
                                }, {
                                    boxLabel: gettext('Not using Devilry'),
                                    name: 'delivery_types',
                                    cls: 'deliveryTypesNonElectronic',
                                    inputValue: 1
                                }]
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                margin: '0 0 0 3',
                                html: [
                                    '<p class="muted"><small>',
                                        gettext('If you only use Devilry to give feedback, and students deliver paper copies or through an alternative channel (oral presentation, email, ...), choose <em>Not using Devilry</em>.'),
                                    '</small></p>'
                                ].join('')
                            }]

                        }, {
                            // First deadline
                            xtype: 'container',
                            //columnWidth: 0.5,
                            width: 300,
                            items: [{
                                xtype: 'devilry_extjsextras-datetimefield',
                                cls: 'firstDeadlineField',
                                itemId: 'firstDeadlineField',
                                name: 'first_deadline',
                                allowBlank: false,
                                width: 300,
                                fieldLabel: gettext('Submission date')
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                itemId: 'firstDeadlineHelp',
                                margin: '0 0 0 0',
                                html: [
                                    '<p class="muted"><small>',
                                        gettext('Students must submit their delivery before this time.'),
                                    '</small></p>'
                                ].join('')
                            }]
                        }]

                    }, {
                        xtype: 'panel',
                        cls: 'devilry_discussionview_container',
                        
                        items: [{
                            xtype: 'panel',
                            id: 'advancedOptionsPanel',
                            title: [
                                '<div class="bootstrap">',
                                    '<span class="linklike">',
                                        gettext('Advanced options'),
                                    '</span>',
                                    '<small> (',
                                        gettext('click to expand'),
                                    ')</small>',
                                '</div>'
                            ].join(''),
                            collapsible: true,
                            collapsed: true,
                            animCollapse: false,
                            titleCollapse: true,
                            bodyPadding: 20,
                            defaults: {
                                margin: '20 0 0 0'
                            },
                            items: [{
                                // Anonymous?
                                xtype: 'checkboxfield',
                                margin: '0 0 0 0',
                                name: 'anonymous',
                                cls: 'anonymousField',
                                labelAlign: 'left',
                                boxLabel: gettext('Anonymous?')
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                margin: '0 0 0 0',
                                html: [
                                    '<p class="muted"><small>',
                                        gettext('For exams, this should normally be checked. If an assignment is anonymous, examiners see candidate-id instead of any personal information about the students.'),
                                    '</small></p>'
                                ].join('')

                                // Publishing time
                            }, {
                                xtype: 'devilry_extjsextras-datetimefield',
                                width: 300,
                                fieldLabel: gettext('Publishing time'),
                                name: "publishing_time",
                                cls: 'publishingTimeField'
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                margin: '0 0 0 0',
                                itemId: 'publishingTimeHelp',
                                html: [
                                    '<p class="muted"><small>',
                                        gettext('Choose a time when students will be able to start adding deliveries to the assignment. Note that students must be registered on the assignment before they can add any deliveries. You have the option to add students on the next page.'),
                                    '</small></p>'
                                ].join('')
                            }]
                        }]
                    }],


                    fbar: [{
                        xtype: 'button',
                        itemId: 'nextButton',
                        cls: 'createnewassignmentform_nextbutton',
                        text: gettext('Next'),
                        scale: 'large',
                        formBind: true, //only enabled once the form is valid
                        disabled: true
                    }]
                }, {
                    xtype: 'panel',
                    itemId: 'pageTwo',
                    cls: 'page2',
                    border: false,
                    bodyPadding: '0 0 30 0',
                    items: [{

                        // Setup students
                        xtype: 'container',
                        itemId: 'setupStudentsContainer',
                        layout: 'column',
                        items: [{
                            margin: 0,
                            xtype: 'box',
                            width: sideheading_width,
                            cls: 'bootstrap',
                            tpl: [
                                '<h2 {sideheading_attrs}>',
                                    gettext('Students?'),
                                '</h2>'
                            ],
                            data: {
                                sideheading_attrs: sideheading_attrs
                            }
                        }, {
                            xtype: 'radiogroup',
                            columnWidth: 1,
                            itemId: 'studentsSetupRadiogroup',
                            vertical: true,
                            columns: 1,
                            margin: 0,
                            items: [{
                                boxLabel: gettext('Add all students.'),
                                checked: true,
                                margin: 0,
                                name: 'setupstudents_mode',
                                itemId: 'setupStudentsAllRelatedRadio',
                                cls: 'extrastronglabel setupStudentsAllRelatedRadio',
                                inputValue: 'allrelated'
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                tpl: [
                                    '<p class="muted"><small>',
                                        gettext('You may want to view and edit <a {relatedstudents_link}>students</a>.'),
                                    '</small></p>'
                                ],
                                data: {
                                    relatedstudents_link: Ext.String.format('href="{0}" target="_blank" class="new-window-link"',
                                        devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id))
                                }

                            }, {
                                boxLabel: gettext('Copy from another assignment.'),
                                margin: '10 0 0 0',
                                name: 'setupstudents_mode',
                                itemId: 'setupStudentsCopyFromAssignmentRadio',
                                cls: 'extrastronglabel setupStudentsCopyFromAssignmentRadio',
                                hidden: true,
                                inputValue: 'copyfromassignment'
                            }, {
                                xtype: 'container',
                                itemId: 'selectAssignmentToCopyStudentsFrom',
                                layout: 'column',
                                hidden: true,
                                margin: '5 0 0 17',
                                items: [{
                                    xtype: 'selectsingleassignment',
                                    name: 'copyfromassignment_id',
                                    cls: 'copyFromAssignmentIdField',
                                    width: 300
                                }, {
                                    xtype: 'checkboxfield',
                                    name: 'only_copy_passing_groups',
                                    cls: 'onlyCopyPassingGroupsField',
                                    columnWidth: 1,
                                    margin: '0 0 0 10',
                                    checked: false,
                                    boxLabel: gettext('Only copy those with passing grade?')
                                }]

                            }, {
                                boxLabel: gettext('Do not add students at this time.'),
                                margin: '10 0 0 0',
                                name: 'setupstudents_mode',
                                cls: 'extrastronglabel setupStudentsDoNotSetupRadio',
                                inputValue: 'do_not_setup'
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                html: [
                                    '<p class="muted"><small>',
                                        gettext('If you choose not to add students at this time, you will have to add them manually to the assignment later. If you plan for students to work in project groups, you should still add them to the assignment now. You can organize them in project groups at any time, even after they have made deliveries.'),
                                    '</small></p>'
                                ].join('')
                            }]
                        }]

                        // Autosetup examiners
                    }, {
                        xtype: 'container',
                        itemId: 'setupExaminersContainer',
                        cls: 'setupExaminersContainer',
                        margin: '30 0 0 0',
                        layout: 'column',
                        items: [{
                            margin: 0,
                            xtype: 'box',
                            cls: 'bootstrap',
                            width: sideheading_width,
                            padding: '0 30 0 0',
                            tpl: [
                                '<h2 {sideheading_attrs}>',
                                    gettext('Examiners?'),
                                '</h2>',
                                '<p class="muted">',
                                    '<small><em>',
                                        gettext('The people that provide feedback to students'),
                                    '</em></small>',
                                '</p>'
                            ],
                            data: {
                                sideheading_attrs: sideheading_attrs
                            }
                        }, {
                            xtype: 'radiogroup',
                            columnWidth: 1,
                            itemId: 'examinersSetupRadiogroup',
                            vertical: true,
                            columns: 1,
                            margin: 0,
                            items: [{
                                margin: '0 0 0 0',
                                name: 'setupexaminers_mode',
                                checked: true,
                                cls: 'extrastronglabel setupExaminersByTagsRadio',
                                inputValue: 'bytags',
                                itemId: 'setupExaminersByTagsRadio',
                                boxLabel: gettext('Setup examiners by tags.')
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                itemId: 'setupExaminersByTagsHelp',
                                tpl: [
                                    '<p class="muted"><small>',
                                        gettext('Add examiners to students that have at least one tag in common with the examiner.'),
                                        ' ',
                                        gettext('E.g.: If you tag two examiners and 20 students with <em>group1</em>, those two examiners will be set up to correct those 20 students.'),
                                        ' ',
                                        gettext('You may want to view and edit tags for <a {relatedstudents_link}>students</a> and <a {relatedexaminers_link}>examiners</a>.'),
                                    '</small></p>'
                                ],
                                data: {
                                    relatedstudents_link: Ext.String.format('href="{0}" target="_blank" class="new-window-link"',
                                        devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.period_id)),
                                        relatedexaminers_link: Ext.String.format('href="{0}" target="_blank" class="new-window-link"',
                                            devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(this.period_id))
                                }

                            }, {
                                margin: '10 0 0 0',
                                name: 'setupexaminers_mode',
                                hidden: true,
                                itemId: 'setupExaminersCopyFromAssignmentRadio',
                                cls: 'extrastronglabel setupExaminersCopyFromAssignmentRadio',
                                inputValue: 'copyfromassignment',
                                boxLabel: 'X' // Set by the controller

                            }, {
                                boxLabel: gettext('Make me examiner for all students.'),
                                margin: '10 0 0 0',
                                name: 'setupexaminers_mode',
                                cls: 'extrastronglabel setupExaminersMakeAuthuserExaminer',
                                inputValue: 'make_authenticated_user_examiner'
                            }, {
                                xtype: 'box',
                                cls: 'bootstrap',
                                html: [
                                    '<p class="muted"><small>',
                                        gettext('I.e.: you plan to provide feedback to all students yourself.'),
                                    '</small></p>'
                                ].join('')

                            }, {
                                boxLabel: gettext('Do not setup examiners at this time.'),
                                margin: '10 0 0 0',
                                name: 'setupexaminers_mode',
                                cls: 'extrastronglabel setupExaminersDoNotSetupRadio',
                                inputValue: 'do_not_setup'
                            }]
                        }]
                    }],
                    fbar: [{
                        xtype: 'button',
                        itemId: 'backButton',
                        text: gettext('Back'),
                        scale: 'medium'
                    }, '->', {
                        xtype: 'createbutton',
                        minWidth: 200,
                        text: gettext('Create new assignment'),
                        itemId: 'createButton',
                        scale: 'large',
                        formBind: true, //only enabled once the form is valid
                        disabled: true
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
