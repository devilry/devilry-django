/**
 * Defines a box of admins and inherited admins on a basenode.
 * */
Ext.define('devilry_subjectadmin.view.AdminsBox', {
    extend: 'Ext.Panel',
    alias: 'widget.adminsbox',
    bodyCls: 'devilry_adminsbox bootstrap',
    title: gettext('Administrators'),
    ui: 'lookslike-parawitheader-panel',
    requires: ['devilry_subjectadmin.utils.UrlLookup'],

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
        gettext('Inherited:'),
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
            xtype: 'box',
            tpl: this.adminsTpl,
            data: {
                path: path,
                admins: basenodeRecord.get('admins')
            }
        }, {
            xtype: 'box',
            tpl: this.inheritedAdminsTpl,
            data: {
                inherited_admins: this._get_inherited_with_urls(basenodeRecord)
            }
        }]);
    }
});
