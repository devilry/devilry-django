/**
 * Defines a box of admins and inherited admins on a basenode.
 * */
Ext.define('devilry_subjectadmin.view.AdminsBox', {
    extend: 'Ext.Container',
    alias: 'widget.adminsbox',
    cls: 'devilry_subjectadmin_adminsbox bootstrap',
    requires: [
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_subjectadmin.view.ManageAdminsPanel',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_extjsextras.AutoSizedWindow'
    ],

    adminsTpl: [
        '<tpl if="admins.length &gt; 0">',
            '<ul class="devilry_subjectadmin_administratorlist">',
                '<tpl for="admins">',
                    '<li class="administratorlistitem administratorlistitem_{username}">',
                        '<a href="mailto:{email}">',
                            '<tpl if="full_name != null">',
                                '{full_name}',
                            '</tpl>',
                            '<tpl if="full_name == null">',
                                '{username}',
                            '</tpl>',
                        '</a>',
                    '</li>',
                '</tpl>',
            '</ul>',
        '</tpl>',
        '<tpl if="admins.length == 0">',
            '<p><small class="muted">', gettext('No administrators') ,'</small></p>',
        '</tpl>'
    ],
    inheritedAdminsTpl: [
        '<tpl if="inherited_admins.length &gt; 0">',
            '<small class="muted">(',
                gettext('The links in parenthesis is to the location where the administrator is inherited from'),
            ')</p>',
            '<ul class="devilry_subjectadmin_inherited_administratorlist">',
                '<tpl for="inherited_admins">',
                    '<li class="inherited_administratorlistitem inherited_administratorlistitem_{user.username}">',
                        '<a href="mailto:{user.email}">',
                            '<tpl if="user.full_name != null">',
                                '{user.full_name}',
                            '</tpl>',
                            '<tpl if="user.full_name == null">',
                                '{user.username}',
                            '</tpl>',
                        '</a>',
                        ' <small>(<a href="{url}">{basenode.path}</a>)</small>',
                    '</li>',
                '</tpl>',
            '</ul>',
        '</tpl>',
        '<tpl if="inherited_admins.length == 0">',
            '<p><small class="muted">', gettext('No administrators') ,'</small></p>',
        '</tpl>'
    ],


    _get_inherited_with_urls: function(basenodeRecord) {
        var inherited_admins = Ext.clone(basenodeRecord.get('inherited_admins'));
        Ext.Array.each(inherited_admins, function(admin) {
            admin.url = devilry_subjectadmin.utils.UrlLookup.overviewByType(admin.basenode.type, admin.basenode.id);
        }, this);
        return inherited_admins;
    },

    initComponent: function() {
        this.callParent(arguments);
        this.add({
            xtype: 'box',
            html: gettext('Loading') + ' ...'
        });
    },

    /**
     * @param {Object} basenodeRecord (required)
     * A basenode record with ``admins`` and ``inherited_admins`` fields.
     */
    setBasenodeRecord: function(basenodeRecord) {
        this.setLoading(false);
        this.basenodeRecord = basenodeRecord;
        this._updateView();
    },

    _updateView: function() {
        this.removeAll();
        var sorted_admins = Ext.clone(this.basenodeRecord.get('admins'));
        var sorted_admins = sorted_admins.sort(function(a, b) {
            var aKey = a.full_name || a.username;
            var bKey = b.full_name || b.username;
            return aKey.localeCompare(bKey);
        });
        
        this.add([{
            xtype: 'editablesidebarbox',
            title: gettext('Administrators'),
            bodyTpl: this.adminsTpl,
            bodyData: {
                admins: sorted_admins
            },
            listeners: {
                scope: this,
                edit: this._onEdit
            }
        }, {
            xtype: 'container',
            margin: '10 0 0 0',
            cls: 'bootstrap',
            items: [{
                xtype: 'box',
                itemId: 'title',
                tpl: '<h4>{title}</h4>',
                data: {
                    title: gettext('Inherited administrators'),
                }
            }, {
                xtype: 'box',
                tpl: this.inheritedAdminsTpl,
                data: {
                    inherited_admins: this._get_inherited_with_urls(this.basenodeRecord)
                }
            }]
        }]);
    },

    _onEdit: function() {
        Ext.widget('devilry_extjsextras_autosizedwindow', {
            closable: true,
            width: 950,
            height: 550,
            maximizable: false,
            modal: true,
            title: gettext('Edit administrators'),
            layout: 'border',
            items: [{
                xtype: 'manageadminspanel',
                region: 'center',
                basenodeRecord: this.basenodeRecord,
                listeners: {
                    scope: this,
                    usersAdded: function(userRecords) {
                        this._updateView();
                    },
                    usersRemoved: function(userRecords) {
                        this._updateView();
                    }
                }
            }, {
                xtype: 'panel',
                region: 'east',
                width: 250,
                bodyPadding: '20',
                bodyCls: 'bootstrap',
                autoScroll: true,
                border: false,
                tpl: [
                    '<p>',
                        gettext('Use the field at the bottom of this window to search for users. When you select a user from the search results, they are immediatly made administrator. Close the window or hit ESC when you are finished.'),
                    '</p>',
                    '<p>',
                        gettext('Select one or more users and click the remove-button to remove them from administrators.'),
                    '</p>',
                    '<p>',
                        '<span class="text-warning">',
                            gettext('You can remove yourself from administrators.'),
                        '</span> ',
                        '<small class="muted">',
                            gettext('If you remove yourself by accident, you need to ask another administrator to re-add you. Close this window and use the list of administrators and inherited administrators to get in touch with them.'),
                        '</small>',
                    '</p>'
                ],
                data: {}
            }]
        }).show();
    }
});
