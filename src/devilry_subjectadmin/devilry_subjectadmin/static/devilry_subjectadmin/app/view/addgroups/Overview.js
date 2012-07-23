Ext.define('devilry_subjectadmin.view.addgroups.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.addgroupsoverview',
    cls: 'devilry_subjectadmin_addstudentspanel',
    requires: [
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.GridMultiSelectModel',
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    /**
     * @cfg {Object} [assignment_id] (required)
     */

    /**
     * @cfg {String} [on_save_success_url] (required)
     */


    initComponent: function() {
        this.userCellTemplate = new Ext.XTemplate(
            '<div class="userinfo">',
                '<div class="full_name"><strong>',
                    '<tpl if="full_name">',
                        '{full_name}',
                    '<tpl else>',
                        gettext('Full name missing'),
                    '</tpl>',
                '</strong></div>',
                '<div class="username"><small>{username}</small></div>',
            '</div>'
        );
        this.tagsAndExaminersCellTemplate = new Ext.XTemplate(
            '<ul class="unstyled">',
                '<tpl for="tagsAndExaminers">',
                    '<li>',
                        '{tag}: <small>',
                        '<tpl for="examiners">',
                            '<tpl if="data.user.full_name">',
                                '{data.user.full_name}',
                            '<tpl else>',
                                '{data.user.username}',
                            '</tpl>',
                            '<tpl if="xindex != xcount">, </tpl>',
                        '</tpl></small>',
                    '</li>',
                '</tpl>',
            '</ul>'
        );
        this.tagsCellTemplate = new Ext.XTemplate(
            '<ul class="unstyled">',
                '<tpl for="tags">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>'
        );


        Ext.apply(this, {
            layout: 'border',
            title: gettext('Add students'),
            buttons: [{
                xtype: 'checkbox',
                itemId: 'allowDuplicatesCheckbox',
                boxLabel: gettext('Allow duplicates'),
                tooltip: gettext('Check this to allow students to be in more than one group. Checking this stops hiding students that are already in a group on this assignment from the list. The use-case for this feature is if you have project assignments where students are in more than one project group. <strong>Keep this unchecked if you are unsure of what to do</strong>.')
            }, '->', {
                xtype: 'checkbox',
                itemId: 'includeTagsCheckbox',
                checked: true,
                boxLabel: gettext('Include tags'),
                tooltip: gettext('Check this to tag the added students with the tags they have on the period. Keep this checked if you are unsure of what to do. When this is checked, tags are displayed in the second column of the table.')
            }, {
                xtype: 'checkbox',
                checked: true,
                tooltip: gettext('Check this to automatically set examiners that have at least one tag in common with a student as their examiner on this assignment. When this is checked, the result of the tag-matching is displayed in the second column of the table.'),
                itemId: 'automapExaminersCheckbox',
                boxLabel: gettext('Autoset examiners by tags')
            }, {
                xtype: 'primarybutton',
                itemId: 'saveButton',
                text: gettext('Add selected students')
            }]
        });
        this.callParent(arguments);
    },

    setBody: function(config) {
        this.removeAll();
        this.ignoredcount = config.ignoredcount;
        var allIgnored = config.allIgnored;
        this.relatedExaminersMappedByTag = config.relatedExaminersMappedByTag;
        this.periodinfo = config.periodinfo;

        if(allIgnored) {
            this.add([{
                xtype: 'panel',
                region: 'center',
                autoScroll: true,
                bodyPadding: 20,
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: this._getAllIgnoredHelp()
                }]
            }]);
        } else {
            var selModel = Ext.create('devilry_extjsextras.GridMultiSelectModel');
            this.add([{
                xtype: 'grid',
                region: 'center',
                store: 'RelatedStudentsRo',
                selModel: selModel,
                columns: this._getGridColumns()
            }, {
                xtype: 'panel',
                region: 'east',
                autoScroll: true,
                width: 250,
                bodyPadding: 20,
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: this._getHelp()
                }]
            }]);
        }
    },


    _getGridColumns: function() {
        var includeTags = this.down('#includeTagsCheckbox').getValue();
        var automapExaminers = this.down('#automapExaminersCheckbox').getValue();
        var showTagsAndExaminersCol = false;
        var showTagsCol = false;
        if(includeTags && automapExaminers) {
            showTagsAndExaminersCol = true;
        } else if(includeTags) {
            showTagsCol = true
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


    _getHelp: function() {
        return Ext.create('Ext.XTemplate',
            '<p>',
                gettext('Choose the students you want to add on the assignment, and click {savebuttonlabel}.'),
            '</p>',
            '<tpl if="hasIgnored"><p>',
                gettext('<strong>{ignoredcount}</strong> students are not available in the list because they are already registered on the assignment.'),
            '</p></tpl>',
            '<p>',
                gettext('Only students registered on <em>{periodpath}</em> is available in the list.'),
            '</p>',
            '<p><a target="_blank" href="{manageRelatedStudentsUrl}">',
                gettext('Add or edit students on {periodpath}'),
            '</a></p>'
        ).apply({
            periodpath: this.periodinfo.path,
            hasIgnored: this.ignoredcount > 0,
            ignoredcount: this.ignoredcount,
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.periodinfo.id),
            savebuttonlabel: Ext.String.format('<em>{0}</em>', gettext('Add selected students'))
        })
    },

    _getAllIgnoredHelp: function() {
        return Ext.create('Ext.XTemplate',
            '<p>',
                gettext('All students registered on <strong>{periodpath}</strong> is already registered on the assignment. Use the link below to go to {periodpath} and add more students.'),
            '</p>',
            '<p><strong><a target="_blank" href="{manageRelatedStudentsUrl}">',
                gettext('Add more students to {periodpath}'),
            '</a></strong> <small>(', gettext('Opens in new window') ,')</small></p>',
            '<p>',
                gettext('When you return to this page, reload it to see newly added students.'),
            '</p>'
        ).apply({
            periodpath: this.periodinfo.path,
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.periodinfo.id)
        });
    },


    _renderUserCell: function(unused1, unused2, relatedStudentRecord) {
        return this.userCellTemplate.apply(relatedStudentRecord.get('user'));
    },

    _renderTagsCell: function(unused1, unused2, relatedStudentRecord) {
        return this.tagsCellTemplate.apply({
            tags: relatedStudentRecord.getTagsAsArray()
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
            tagsAndExaminers: tagsAndExaminers
        });
    }
});
