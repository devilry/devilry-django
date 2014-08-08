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
        'devilry_extjsextras.AutoSizedWindow',
        'devilry_extjsextras.MarkupMoreInfoBox'
    ],

    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },

    adminsTpl: [
        '<h4>', gettext('Administrator rights'), '</h4>',
        '<p class="muted">',
            '<small>',
                gettext('{admincount} users have administrator rights on this item.'),
                ' {MORE_BUTTON}',
            '</small>',
        '</p>',
        '<div {MORE_ATTRS}>',
            '<h5>', gettext('How administrator rights work'), '</h5>',
            '<p>',
                gettext('Devilry has a very simple permission system for administrators. You are either administrator on an item, or you have no access to the administrator views for an item.'),
            '</p>',
            '<p>',
                gettext('Administrators can be set anywhere in the hierarchy, from nodes on the top, to assignments at the bottom, and permissions propagate downwards in the hierarchy.'),
            '</p>',

            '<h5>', gettext('Administrators on this item') ,'</h5>',
            '<tpl if="admins.length &gt; 0">',
                '<p><small class="muted">',
                    gettext('These are the administrators on this item.'),
                '</small></p>',
                '<ul class="devilry_subjectadmin_administratorlist unstyled">',
                    '<tpl for="admins">',
                        '<li class="administratorlistitem administratorlistitem_{username}">',
                            '<a href="mailto:{email}" class="mail-link-right">',
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
                '<p>',
                    ' <a href="#" class="btn editadmins_link">',
                        gettext('Add or edit administrators'),
                    '</a>',
                '</p>',
            '<tpl else>',
                '<p>',
                    '<small class="muted">', gettext('No administrators') ,'</small>',
                '</p>',
                '<p>',
                    ' <a href="#" class="btn editadmins_link">',
                        gettext('Add administrators'),
                    '</a>',
                '</p>',
            '</tpl>',

            '<tpl if="inherited_admins.length &gt; 0">',
                '<h5>', gettext('Other administrators'), '</h5>',
                '<ul class="devilry_subjectadmin_inherited_administratorlist unstyled">',
                    '<tpl for="inherited_admins">',
                        '<li class="inherited_administratorlistitem inherited_administratorlistitem_{user.username}">',
                            '<a href="mailto:{user.email}" class="mail-link-right">',
                                '<tpl if="user.full_name != null">',
                                    '{user.full_name}',
                                '</tpl>',
                                '<tpl if="user.full_name == null">',
                                    '{user.username}',
                                '</tpl>',
                            '</a>',
                            ' <tpl if="basenode.is_admin">',
                                '<small>(<a href="{url}">{basenode.path})</a></small>',
                            '<tpl else>',
                                '<small class="muted">({basenode.path})</small>',
                            '</tpl>',
                        '</li>',
                    '</tpl>',
                '</ul>',
            '</tpl>',
        '<div>'
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
        sorted_admins = sorted_admins.sort(function(a, b) {
            var aKey = a.full_name || a.username;
            var bKey = b.full_name || b.username;
            return aKey.localeCompare(bKey);
        });
        
        var inherited_admins = this._get_inherited_with_urls(this.basenodeRecord);
        this.add([{
            xtype: 'markupmoreinfobox',
            moreCls: '',
            moretext: gettext('Details'),
            lesstext: gettext('Hide details'),
            tpl: this.adminsTpl,
            data: {
                admins: sorted_admins,
                inherited_admins: inherited_admins,
                admincount: sorted_admins.length + inherited_admins.length
            },
            listeners: {
                scope: this,
                element: 'el',
                delegate: 'a.editadmins_link',
                click: function(e) {
                    e.preventDefault();
                    this._onEdit();
                }
            }
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
                            gettext('If you remove yourself by accident, you need to ask another administrator to re-add you. Close this window and use the list of administrators and other administrators to get in touch with them.'),
                        '</small>',
                    '</p>'
                ],
                data: {}
            }]
        }).show();
    }
});
