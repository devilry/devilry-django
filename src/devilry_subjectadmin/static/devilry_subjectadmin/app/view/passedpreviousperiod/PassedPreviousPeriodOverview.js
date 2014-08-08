Ext.define('devilry_subjectadmin.view.passedpreviousperiod.PassedPreviousPeriodOverview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.passedpreviousperiodoverview',
    cls: 'devilry_subjectadmin_passedpreviousperiodoverview',
    requires: [
        'devilry_subjectadmin.view.passedpreviousperiod.SelectGroupsGrid',
        'devilry_subjectadmin.view.passedpreviousperiod.ConfirmGroupsGrid',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.AlertMessage',
        'devilry_extjsextras.MarkupMoreInfoBox'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */

    // Internal attribute used for the width of the west-panel on all pages
    sideBarWidth: 300,

    initComponent: function() {
        Ext.apply(this, {
            padding: '20 40 20 40',
            layout: 'border',
            style: 'background: transparent !important;',

            items: [{
                xtype: 'box',
                region: 'north',
                height: 55,
                cls: 'bootstrap',
                html: [
                    '<h1 style="margin: 0; padding: 0;">',
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
                    style: 'background: transparent !important;',
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
                            cls: 'nextButton',
                            disabled: true,
                            itemId: 'nextButton'
                        }]
                    }, {
                        xtype: 'markupmoreinfobox',
                        region: 'west',
                        autoScroll: true,
                        width: this.sideBarWidth,
                        cls: 'bootstrap',
                        padding: '0 30 0 0',
                        moretext: gettext('More help'),
                        lesstext: gettext('Less help'),
                        tpl: [
                            '<p>',
                                gettext('Select one or more groups. Groups that we belive have passed this assignment before has been selected automatically, and they are marked with the name of the old {period_term}.'),
                            '</p>',
                            '<p>{MORE_BUTTON}</p>',
                            '<div {MORE_ATTRS}>',
                                '<p>',
                                    gettext('The search for previously passed students match the short name of old assignments against the short name of this assignment. Only groups with exactly one student in both the old and the current assignment is matched. You can find the short name of an assignment by looking at the breadcrumb in the header, or in the title of the Rename-section of "Dangerous actions" when visiting the assignment.'),
                                '</p>',
                            '</div>'
                        ],
                        data: {
                            period_term: gettext('period')
                        }
                    }]
                }, {
                    xtype: 'container',
                    itemId: 'pageTwo',
                    style: 'background: transparent !important;',
                    layout: 'border',
                    items: [{
                        xtype: 'markupmoreinfobox',
                        region: 'west',
                        width: this.sideBarWidth,
                        cls: 'bootstrap pageTwoSidebar',
                        padding: '0 30 0 0',
                        autoScroll: true,
                        itemId: 'pageTwoSidebar',
                        moretext: gettext('More help'),
                        lesstext: gettext('Less help'),
                        tpl: [
                            '<p>',
                                gettext('Make sure you really want to mark these groups as previously passed before saving.'),
                            '</p>',

                            '<tpl if="needsGradeFormatExplained">',
                                '<div class="gradeformat-help">',
                                    '<h4>',
                                        gettext('Grade format'),
                                    '</h4>',
                                    '<p>',
                                        gettext('The current grading system, {gradingsystem}, specifies the following help:'),
                                        ' <blockquote class="text-info shorthelp">{shorthelp}</blockquote>',
                                    '</p>',
                                    '<p>',
                                        '<span class="text-warning">', gettext('Warning'), ':</span>',
                                        '<small> ',
                                            gettext('You must specify passing grades. Many users find it confusing when the autodetected grade is not a passing grade, but that is simply because the grading system has been configured differently this {period_term}.'),
                                        '</small>',
                                    '</p>',
                                '</div>',
                            '</tpl>',
                            '<p>{MORE_BUTTON}</p>',

                            '<div {MORE_ATTRS}>',
                                '<tpl if="needsGradeFormatExplained">',
                                '<h4>',
                                    gettext('Grade'),
                                '</h4>',
                                    '<tpl if="!loading">',
                                        '<p>',
                                            gettext('You have to specify a grade for each group. You do so by clicking the cells in the Grade-column and specifying a grade. If Devilry autodetected that the group has passed this assignment previously, the grade will already be specified, but you can still override the detected value if you grade students differently this {period_term}.'),
                                        '</p>',
                                    '</tpl>',
                                '</tpl>',

                                '<h4>',
                                    gettext('How it works'),
                                '</h4>',
                                '<p>',
                                    gettext('When you click save, we will create a new delivery for each of the groups, mark the delivery as a placeholder for a previously approved delivery, and create a feedback on the delivery. The grade of the feedback will be the one specified in the Grade-column.'),
                                '</p>',
                            '</div>'
                        ],
                        data: {
                            loading: true
                        }
                    }, {
                        xtype: 'panel',
                        itemId: 'confirmGridWrapper',
                        layout: 'fit',
                        items: [],
                        region: 'center',
                        fbar: [{
                            xtype: 'button',
                            text: gettext('Back'),
                            scale: 'large',
                            itemId: 'backButton'
                        }, '->', {
                            xtype: 'primarybutton',
                            text: gettext('Save'),
                            itemId: 'saveButton',
                            cls: 'saveButton'
                        }]
                    }]
                }, {
                    itemId: 'unsupportedGradeEditor',
                    xtype: 'alertmessage',
                    type: 'error',
                    title: 'Unsupported grading system',
                    messagetpl: gettext('The passed previously functionality is not supported by the grading system configured on this assignment ({gradingsystem}).'),
                    messagedata: {
                        gradingsystem: gettext('Loading') + ' ...'
                    }
                }]
            }]
        });
        this.callParent(arguments);
    }
});
