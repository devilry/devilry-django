/**
 * Defines a box of admins and inherited admins on a basenode.
 * */
Ext.define('devilry_subjectadmin.view.AdminsBox', {
    extend: 'Ext.Container',
    alias: 'widget.adminsbox',
    cls: 'devilry_subjectadmin_adminsbox bootstrap',
    requires: [
        'Ext.window.Window',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_subjectadmin.view.ManageAdminsPanel',
        'devilry_extjsextras.EditableSidebarBox'
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
        Ext.widget('window', {
            layout: 'fit',
            closable: true,
            width: 700,
            height: 500,
            maximizable: true,
            modal: true,
            title: gettext('Edit administrators'),
            items: {
                xtype: 'manageadminspanel',
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
            }
        }).show();
    }
});
