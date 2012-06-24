/**
 * Defines a box of admins and inherited admins on a basenode.
 * */
Ext.define('devilry_subjectadmin.view.AdminsBox', {
    extend: 'Ext.Panel',
    alias: 'widget.adminsbox',
    bodyCls: 'devilry_adminsbox bootstrap',
    title: gettext('Administrators'),
    ui: 'lookslike-parawitheader-panel',

    tpl: [
        '<tpl if="loading">',
            '{loading}',
        '</tpl>',
        '<tpl if="!loading">',
            '{path}:',
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
            gettext('Inherited:'),
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
                        ' ({basenode.path})',
                    '</li>',
                '</tpl>',
            '</ul>',
        '</tpl>'
    ],

    initComponent: function() {
        this.data = {
            loading: gettext('Loading ...')
        };
        this.callParent(arguments);
    },

    /**
     * @param {Object} basenodeRecord (required)
     * A basenode record with ``admins`` and ``inherited_admins`` fields.
     *
     * @param {string} path (required)
     * The unique path to the basenode.
     */
    setBasenodeRecord: function(basenodeRecord, path) {
        console.log(basenodeRecord.get('inherited_admins'));
        this.update({
            loading: false,
            path: path,
            admins: basenodeRecord.get('admins'),
            inherited_admins: basenodeRecord.get('inherited_admins')
        });
    }
});
