Ext.define('devilry_subjectadmin.view.addgroups.AddGroups', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.addgroupspanel',
    cls: 'devilry_subjectadmin_addgroupspanel',
    requires: [
        'Ext.XTemplate',
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.GridMultiSelectModel',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.MarkupMoreInfoBox',
        'devilry_subjectadmin.view.managestudents.TagsHelp',
        'devilry_extjsextras.form.DateTimeField'
    ],

    /**
     * @cfg {Object} [assignment_id] (required)
     */

    /**
     * @cfg {String} [on_save_success_url] (required)
     */

    /**
     * @cfg {String} [breadcrumbtype] (required)
     * See controller.AddGroups._setBreadcrumb
     */

    helptpl: [
        '<p class="muted">',
            gettext('Choose the students you want to add to the assignment, and click {savebuttonlabel}.'),
            '<br/><small> {MORE_BUTTON}</small>',
        '</p>',
        '<div {MORE_ATTRS}>',
            '<p>',
                gettext('Move your mouse over the checkboxes for help.'),
            '</p>',
            '<h3>', gettext('Missing students?'), '</h3>',
            '<p>',
                gettext('Only students registered on {periodpath} is available in the list.'),
            '</p>',
            '<tpl if="is_periodadmin">',
                '<p>',
                    '<a target="_blank" href="{manageRelatedStudentsUrl}" class="addoreditstudents_link new-window-link">',
                        gettext('Add or edit students on {periodpath}'),
                    '</a>',
                '</p>',
                '<p class="muted"><small>',
                    gettext('You need to reload this page when you return after adding students.'),
                '</small></p>',
            '<tpl else>',
                '<p class="text-warning">',
                    gettext('You do not have administrator rights on {periodpath}, so you need to ask someone with administrator rights if you need to add more students than the ones available in the list.'),
                '</p>',
            '</tpl>',

            '<tpl if="hasIgnored">',
                '<h3>', gettext('Allow duplicates?'), '</h3>',
                '<p>',
                    gettext('<strong>{ignoredcount}</strong> students are not available in the list because they are already registered on the assignment. Select <em>Allow duplicates</em> if you want to allow students to be in multiple groups on the same assignment.'),
                '</p>',
            '</tpl>',

            '<h3>', gettext('Tags'), '</h3>',
            '<p>{tagsintro}</p>',
            '{tagsdetails}',
            '<p>',
                gettext('You can copy tags from {periodpath} when you add students. The tags on {periodpath} and tags on assignments in {periodpath} is not kept in sync after you add students to the assignment, so you can safely edit tags on the assignment without affecting any other assignments or {periodpath}.'),
            '</p>',
        '</div>'
    ],

    initComponent: function() {
        this.userCellTemplate = new Ext.XTemplate(
            '<div class="userinfo userinfo_{username}">',
                '<div class="full_name"><strong>',
                    '<tpl if="full_name"><strong>',
                        '{full_name}',
                    '</strong><tpl else><em>',
                        gettext('Full name missing'),
                    '</em></tpl>',
                '</strong></div>',
                '<div class="username"><small class="muted">{username}</small></div>',
            '</div>'
        );
        this.tagsAndExaminersCellTemplate = new Ext.XTemplate(
            '<ul class="unstyled tags_and_examiners tags_and_examiners_{username}">',
                '<tpl for="tagsAndExaminers">',
                    '<li class="tag_{tag}">',
                        '<span class="tag">{tag}</span>: ',
                        '<small class="examiners muted">',
                            '<tpl if="examiners">',
                                '<tpl for="examiners">',
                                    '<tpl if="data.user.full_name">',
                                        '{data.user.full_name}',
                                    '<tpl else>',
                                        '{data.user.username}',
                                    '</tpl>',
                                    '<tpl if="xindex != xcount">, </tpl>',
                                '</tpl>',
                            '<tpl else>',
                                '<span class="text-warning">', gettext('No matching examiners'), '</em>',
                            '</tpl>',
                        '</small>',
                    '</li>',
                '</tpl>',
            '</ul>'
        );
        this.tagsCellTemplate = new Ext.XTemplate(
            '<ul class="unstyled tags tags_{username}">',
                '<tpl for="tags">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>'
        );


        var selModel = Ext.create('devilry_extjsextras.GridMultiSelectModel');
        Ext.apply(this, {
            layout: 'border',
            bodyPadding: 20,
            items: [{
                xtype: 'grid',
                region: 'center',
                itemId: 'studentsGrid',
                cls: 'bootstrap relatedstudentsgrid',
                store: 'RelatedStudentsRo',
                selModel: selModel,
                columns: this._getGridColumns(),
                tbar: [{
                    text: gettext('Select'),
                    menu: [{
                        text: gettext('Select all'),
                        itemId: 'selectAll'
                    }, {
                        text: gettext('Deselect all'),
                        itemId: 'deselectAll'
                    }]
                }, {
                    xtype: 'addgroupsallowduplicatescheckbox',
                    margin: '0 0 0 20'
                }],
                buttons: ['->', {
                    xtype: 'checkbox',
                    cls: 'includetagscheckbox',
                    itemId: 'includeTagsCheckbox',
                    checked: true,
                    boxLabel: gettext('Include tags'),
                    tooltip: interpolate(gettext('Check this to tag the added students with the tags they have on %(periodpath)s. Keep this checked if you are unsure of what to do. When this is checked, tags are displayed in the second column of the table.'), {
                        periodpath: Ext.String.format('<em>{0}</em>', this.periodinfo.path)
                    }, true)
                }, {
                    xtype: 'checkbox',
                    cls: 'autosetexaminerscheckbox',
                    checked: false,
                    tooltip: gettext('Check this to automatically set examiners that have at least one tag in common with a student as their examiner on this assignment. When this is checked, the result of the tag-matching is displayed in the second column of the table.'),
                    itemId: 'automapExaminersCheckbox',
                    boxLabel: gettext('Autoset examiners by tags')
                }, {
                    xtype: 'primarybutton',
                    cls: 'addselectedbutton',
                    disabled: true,
                    itemId: 'saveButton',
                    text: gettext('Add selected students')
                }]
            }, {
                xtype: 'panel',
                cls: 'sidebarpanel',
                border: false,
                region: 'west',
                autoScroll: true,
                width: 370,
                bodyPadding: '0 40 0 0',
                layout: 'anchor',
                items: [{
                    anchor: '100%',
                    region: 'center',
                    xtype: 'markupmoreinfobox',
                    moretext: gettext('More help') + ' ...',
                    lesstext: gettext('Less help') + ' ...',
                    tpl: this.helptpl,
                    data: {
                        periodpath: this.periodinfo.path,
                        is_periodadmin: this.periodinfo.is_admin,
                        hasIgnored: this.ignoredcount > 0,
                        ignoredcount: this.ignoredcount,
                        manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.periodinfo.id),
                        savebuttonlabel: Ext.String.format('<em>{0}</em>', gettext('Add selected students')),
                        tagsintro: devilry_subjectadmin.view.managestudents.TagsHelp.getIntroText(),
                        tagsdetails: devilry_subjectadmin.view.managestudents.TagsHelp.getDetailsUl()
                    }
                }, {
                    xtype: 'form',
                    margin: '20 0 0 0',
                    anchor: '100%',
                    itemId: 'firstDeadlineForm',
                    border: 0,
                    layout: 'anchor',
                    cls: 'bootstrap',
                    items: [{
                        xtype: 'devilry_extjsextras-datetimefield',
                        fieldLabel: gettext('Submission date'),
                        labelAlign: 'top',
                        labelStyle: 'font-weight: bold',
                        width: 240,
                        cls: 'first_deadline_field',
                        name: 'first_deadline'
                    }, {
                        xtype: 'box',
                        anchor: '100%',
                        html: [
                            '<p class="muted"><small>',
                                gettext('Students must submit their delivery before this time. This becomes their first deadline on this assignment, and it can be edited just like any other deadline.'),
                            '</small></p>'
                        ].join('')
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getGridColumns: function() {
        var includeTags = true;
        var automapExaminers = false;
        var showTagsAndExaminersCol = false;
        var showTagsCol = false;
        if(includeTags && automapExaminers) {
            showTagsAndExaminersCol = true;
        } else if(includeTags) {
            showTagsCol = true;
        }

        var columns = [{
            header: gettext('Name'),
            dataIndex: 'id',
            menuDisabled: true,
            sortable: false,
            flex: 4,
            renderer: Ext.bind(this._renderUserCell, this)
        }, {
            header: gettext('Tags and matching examiners'),
            dataIndex: 'tags',
            menuDisabled: true,
            sortable: false,
            flex: 6,
            hidden: !showTagsAndExaminersCol,
            itemId: 'tagsAndExaminersColumn',
            renderer: Ext.bind(this._renderTagsAndExaminersCell, this)
        }, {
            header: gettext('Tags'),
            dataIndex: 'tags',
            menuDisabled: true,
            sortable: false,
            flex: 4,
            hidden: !showTagsCol,
            itemId: 'tagsColumn',
            renderer: Ext.bind(this._renderTagsCell, this)
        }];
        return columns;
    },

    _renderUserCell: function(unused1, unused2, relatedStudentRecord) {
        return this.userCellTemplate.apply(relatedStudentRecord.get('user'));
    },

    _renderTagsCell: function(unused1, unused2, relatedStudentRecord) {
        return this.tagsCellTemplate.apply({
            tags: relatedStudentRecord.getTagsAsArray(),
            username: relatedStudentRecord.get('user').username
        });
    },

    _renderTagsAndExaminersCell: function(unused1, unused2, relatedStudentRecord) {
        var tags = relatedStudentRecord.getTagsAsArray();
        var tagsAndExaminers = [];
        for(var index=0; index<tags.length; index++)  {
            var tag = tags[index];
            var relatedExaminerRecords = this.relatedExaminersMappedByTag[tag];
            tagsAndExaminers.push({
                tag: tag,
                examiners: relatedExaminerRecords
            });
        }
        return this.tagsAndExaminersCellTemplate.apply({
            tagsAndExaminers: tagsAndExaminers,
            username: relatedStudentRecord.get('user').username
        });
    }
});
