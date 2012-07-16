/**
 * Defines a box of admins and inherited admins on a basenode.
 * */
Ext.define('devilry_subjectadmin.view.AdminsBox', {
    extend: 'Ext.Container',
    alias: 'widget.adminsbox',
    cls: 'devilry_adminsbox bootstrap',
    requires: [
        'Ext.window.Window',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_extjsextras.EditableSidebarBox',
        'devilry_usersearch.ManageUsersPanel'
    ],

    adminsTpl: [
        '{path}: ',
        '<tpl if="admins.length &gt; 0">',
            '<ul class="devilry_administratorlist">',
                '<tpl for="admins">',
                    '<li>',
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
            '<p><em>', gettext('No administrators') ,'</em></p>',
        '</tpl>'
    ],
    inheritedAdminsTpl: [
        '<tpl if="inherited_admins.length &gt; 0">',
            '<ul class="devilry_inherited_administratorlist">',
                '<tpl for="inherited_admins">',
                    '<li>',
                        '<a href="mailto:{user.email}">',
                            '<tpl if="user.full_name != null">',
                                '{user.full_name}',
                            '</tpl>',
                            '<tpl if="user.full_name == null">',
                                '{user.username}',
                            '</tpl>',
                        '</a>',
                        ' (<a href="{url}">{basenode.path}</a>)',
                    '</li>',
                '</tpl>',
            '</ul>',
        '</tpl>',
        '<tpl if="inherited_admins.length == 0">',
            '<p><em>', gettext('No administrators') ,'</em></p>',
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
            html: gettext('Loading ...')
        });
    },

    /**
     * @param {Object} basenodeRecord (required)
     * A basenode record with ``admins`` and ``inherited_admins`` fields.
     *
     * @param {string} path (required)
     * The unique path to the basenode.
     */
    setBasenodeRecord: function(basenodeRecord, path) {
        this.setLoading(false);
        this.removeAll();
        this.add([{
            xtype: 'editablesidebarbox',
            title: gettext('Administrators'),
            bodyTpl: this.adminsTpl,
            data: {
                path: path,
                admins: basenodeRecord.get('admins')
            },
            buttonListeners: {
                scope: this,
                click: this._onEdit
            }
        }, {
            xtype: 'panel',
            margin: {top: 10},
            ui: 'lookslike-parawitheader-panel',
            title: gettext('Inherited administrators'),
            items: [{
                xtype: 'box',
                tpl: this.inheritedAdminsTpl,
                data: {
                    inherited_admins: this._get_inherited_with_urls(basenodeRecord)
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
                xtype: 'manageuserspanel'
            }
        }).show();
    }
});
