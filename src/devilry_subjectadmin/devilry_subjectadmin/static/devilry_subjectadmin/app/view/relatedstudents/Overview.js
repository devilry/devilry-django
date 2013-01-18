/**
 * Related students overview.
 */
Ext.define('devilry_subjectadmin.view.relatedstudents.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.relatedstudents',
    cls: 'devilry_subjectadmin_relatedusers devilry_subjectadmin_relatedstudents',
    requires: [
        'Ext.layout.container.Column',
        'devilry_extjsextras.MoreInfoBox',
        'devilry_subjectadmin.view.relatedstudents.Grid',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.OkCancelPanel',
        'devilry_subjectadmin.view.managestudents.ChooseTagsPanel',
        'devilry_subjectadmin.view.relatedstudents.SelectUserPanel'
    ],

    frame: false,
    border: false,
    bodyPadding: '20 40 20 40',


    /**
     * @cfg {String} period_id (required)
     */


    introhelp: interpolate(gettext('These are the students that can be added to any assignments within this %(period_term)s.'), {
        period_term: gettext('period')
    }, true),
    morehelptpl: [
        '<h3>', gettext('Removing students'), '</h3>',
        '<p>',
            gettext('When you remove a student from this list, Devilry assumes that the student is not planning on completing the {period_term}. This means that they will disappear from any {period_term} summaries, including calculation of final grade on the {period_term}.'),
        '</p>',
        
        '<p>',
            gettext('Removing a student from a {period_term} does not affect any groups, deliveries or feedback already registered on an assignment.'),
        '</p>',

        '<h3>', gettext('Tags'), '</h3>',
        '<p>',
            gettext('Tags is a flexible way of organizing students and examiners. Since both examiners and administrators can see tags, they are a great way of marking students that needs special attention, such as students with special needs.'),
        '</p>',

        '<h4>', gettext('Accociate examiners with students using tags'), '</h4>',
        '<p>',
            gettext('If you tag your students and examiners with the same tags, you can automatically assign examiners to students when creating a new assignment. E.g.: If you tag two examiners and 20 students with <em>group1</em>, those two examiners will be set up to correct those 20 students when you create a new assignment.'),
        '</p>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            bodyStyle: 'background: transparent;',
            items: [{
                xtype: 'box',
                columnWidth: 1,
                cls: 'bootstrap',
                region: 'north',
                height: 50,
                itemId: 'heading',
                tpl: [
                    '<h1 style="margin-top: 0; padding-top: 0;">',
                        gettext('Students'),
                        '<small class="muted"> - ',
                            '<tpl if="periodpath">',
                                '{periodpath}',
                            '<tpl else>',
                                gettext('Loading') ,' ...',
                            '</tpl>',
                        '</small></p>',
                    '</h1>'
                ],
                data: {
                    periodpath: null
                }
            }, {
                xtype: 'panel',
                bodyStyle: 'background: transparent;',
                border: false,
                layout: 'border',
                region: 'center',
                items: [{
                    xtype: 'relatedstudentsgrid',
                    region: 'center',
                    dockedItems: [{
                        xtype: 'toolbar',
                        dock: 'bottom',
                        ui: 'footer',
                        items: [{
                            xtype: 'button',
                            ui: 'danger',
                            scale: 'large',
                            itemId: 'removeButton',
                            cls: 'remove_related_user_button remove_related_student_button',
                            disabled: true,
                            text: gettext('Remove selected')
                        }, '->', {
                            xtype: 'button',
                            scale: 'large',
                            itemId: 'tagsButton',
                            disabled: true,
                            cls: 'related_users_tags_button related_students_tags_button',
                            text: gettext('Tags'),
                            menu: [{
                                text: gettext('Clear tags'),
                                cls: 'clear_tags_button',
                                itemId: 'clearTagsButton'
                            }, {
                                text: gettext('Set tag(s)'),
                                cls: 'set_tags_button',
                                itemId: 'setTagsButton'
                            }, {
                                text: gettext('Add tag(s)'),
                                cls: 'add_tags_button',
                                itemId: 'addTagsButton'
                            }]
                        }, {
                            xtype: 'primarybutton',
                            itemId: 'addButton',
                            tabIndex: 1,
                            cls: 'add_related_user_button add_related_student_button',
                            text: gettext('Add student')
                        }]
                    }],
                    tbar: [{
                        xtype: 'textfield',
                        itemId: 'filterfield',
                        width: 330,
                        emptyText: gettext('Filter (name, username, tags, candidate ID)') + ' ...'
                    }, '->', {
                        xtype: 'box',
                        itemId: 'gridSummaryBox',
                        margin: '0 5 0 0'
                    }]
                }, {
                    xtype: 'container',
                    layout: 'anchor',
                    width: 390,
                    region: 'east',
                    padding: '0 10 0 30',
                    autoScroll: true,
                    items: [{
                        xtype: 'panel',
                        border: false,
                        bodyStyle: 'background: transparent;',
                        layout: 'card',
                        itemId: 'sidebarDeck',
                        items: [{
                            xtype: 'moreinfobox',
                            bodyStyle: 'background: transparent;',
                            cls: 'related_user_helpbox related_student_helpbox',
                            itemId: 'helpBox',
                            introtext: this.introhelp,
                            moretext: gettext('More help ...'),
                            lesstext: gettext('Less help'),
                            moreWidget: {
                                xtype: 'box',
                                tpl: this.morehelptpl,
                                data: {
                                    period_term: gettext('period')
                                }
                            }
                        }, {
                            xtype: 'selectrelateduserpanel',
                            itemId: 'selectRelatedUserPanel'
                        }, {
                            xtype: 'okcancelpanel',
                            itemId: 'confirmRemovePanel',
                            cls: 'removeconfirmpanel bootstrap',
                            oktext: gettext('Remove selected'),
                            okbutton_ui: 'danger',
                            bodyPadding: 10,
                            html: [
                                '<p>',
                                    gettext('Do you really want to remove all the selected students?'),
                                    interpolate(gettext('They will not be removed from any existing assignments. You will not be able to add them on any new assignments, and they will not be available in statistics for the entire %(period_term)s.'), {
                                        period_term: gettext('period')
                                    }, true),
                                '</p>'
                            ].join('')
                        }, {
                            xtype: 'choosetagspanel',
                            initialValue: '',
                            itemId: 'setTagsPanel',
                            cls: 'set_tags_panel',
                            buttonText: gettext('Set tags')
                        }, {
                            xtype: 'choosetagspanel',
                            initialValue: '',
                            itemId: 'addTagsPanel',
                            cls: 'add_tags_panel',
                            buttonText: gettext('Add tags')
                        }, {
                            xtype: 'okcancelpanel',
                            itemId: 'clearTagsPanel',
                            cls: 'clear_tags_panel',
                            oktext: gettext('Clear tags'),
                            okbutton_ui: 'danger',
                            bodyPadding: 10,
                            html: [
                                '<p>',
                                    gettext('Do you really want to clear all tags on the selected students?'),
                                '</p>'
                            ].join('')
                        }]
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
