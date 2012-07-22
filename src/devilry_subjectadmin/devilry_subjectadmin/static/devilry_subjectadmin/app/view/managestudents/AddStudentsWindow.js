/**
 * A window for adding students to an assignment.
 * */
Ext.define('devilry_subjectadmin.view.managestudents.AddStudentsWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.addstudentswindow',
    cls: 'addstudentswindow',
    requires: [
        'devilry_extjsextras.form.Help',
        'devilry_extjsextras.PrimaryButton',
        'devilry_extjsextras.GridMultiSelectModel',
        'devilry_subjectadmin.utils.UrlLookup'
    ],

    /**
     * @cfg {Ext.data.Store} [relatedStudentsStore] (required)
     */

    /**
     * @cfg {Object} [periodinfo] (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'border',
            closable: true,
            width: 700,
            height: 500,
            //maximizable: true,
            modal: true,
            title: gettext('Add students'),
            buttons: [{
                xtype: 'button',
                itemId: 'refreshButton',
                scale: 'medium',
                text: gettext('Refresh')
            }, {
                xtype: 'checkbox',
                itemId: 'allowDuplicatesCheckbox',
                boxLabel: gettext('Allow duplicates')
            }, '->', {
                xtype: 'primarybutton',
                itemId: 'saveButton',
                text: gettext('Add selected students')
            }]
        });
        this.callParent(arguments);
        this.refreshBody();
    },

    refreshBody: function() {
        this.removeAll();
        this.ignoredcount = this.relatedStudentsStore.getTotalCount() - this.relatedStudentsStore.getCount()
        var allIgnored = this.relatedStudentsStore.getTotalCount() == this.ignoredcount;

        var tagsCellTemplate = new Ext.XTemplate(
            '<ul class="unstyled">',
                '<tpl for="tags">',
                    '<li>{.}</li>',
                '</tpl>',
            '</ul>'
        );
        var userCellTemplate = new Ext.XTemplate(
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
                store: this.relatedStudentsStore,
                selModel: selModel,
                columns: [{
                    header: 'Name',
                    dataIndex: 'id',
                    menuDisabled: true,
                    sortable: false,
                    flex: 6,
                    renderer: function(unused1, unused2, relatedStudentRecord) {
                        return userCellTemplate.apply(relatedStudentRecord.get('user'));
                    }
                }, {
                    header: 'Tags',
                    dataIndex: 'tags',
                    menuDisabled: true,
                    sortable: false,
                    flex: 4,
                    renderer: function(unused1, unused2, relatedStudentRecord) {
                        return tagsCellTemplate.apply({
                            tags: relatedStudentRecord.getTagsAsArray()
                        });
                    }
                }],
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
                gettext('Use the refresh button to reload students when you return to this page.'),
            '</p>'
        ).apply({
            periodpath: this.periodinfo.path,
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(this.periodinfo.id)
        });
    }
});
