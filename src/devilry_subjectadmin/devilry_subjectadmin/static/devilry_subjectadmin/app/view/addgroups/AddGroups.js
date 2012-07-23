Ext.define('devilry_subjectadmin.view.addgroups.AddGroups', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.addgroupspanel',
    cls: 'devilry_subjectadmin_addgroupspanel',
    requires: [
        'Ext.XTemplate',
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

    /**
     * @cfg {String} [breadcrumbtype] (required)
     * See controller.AddGroups._setBreadcrumb
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


        var selModel = Ext.create('devilry_extjsextras.GridMultiSelectModel');
        Ext.apply(this, {
            layout: 'border',
            buttons: ['->', {
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
                xtype: 'button',
                scale: 'medium',
                itemId: 'saveButton',
                text: gettext('Add selected students')
            }],
            items: [{
                xtype: 'grid',
                region: 'center',
                store: 'RelatedStudentsRo',
                selModel: selModel,
                columns: this._getGridColumns(),
                tbar: [{
                    text: gettext('Advanced options'),
                    menu: {
                        xtype: 'menu',
                        plain: true,
                        items: [{
                            xtype: 'addgroupsallowduplicatescheckbox'
                        }]
                    }
                }, {
                    text: gettext('Select'),
                    menu: [{
                        text: gettext('Select all'),
                        itemId: 'selectAll'
                    }, {
                        text: gettext('Deselect all'),
                        itemId: 'deselectAll'
                    }]
                }]
            }, {
                xtype: 'panel',
                region: 'east',
                autoScroll: true,
                width: 300,
                bodyPadding: 20,
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: this._getHelp()
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getGridColumns: function() {
        var includeTags = true;
        var automapExaminers = true;
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
