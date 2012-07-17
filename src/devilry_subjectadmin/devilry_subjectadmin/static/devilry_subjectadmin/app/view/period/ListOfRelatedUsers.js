/**
 * Overview of relatated users on a period.
 */
Ext.define('devilry_subjectadmin.view.period.ListOfRelatedUsers' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.listofrelatedusers',
    requires: [
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler',
        'devilry_subjectadmin.view.period.ManageRelatedUsersPanel',
        'devilry_subjectadmin.view.period.ManageRelatedStudentsPanel'
    ],

    listTemplate: [
        '<div class="bootstrap">',
            '<tpl if="users !== undefined">',
                '<tpl if="users.length == 0">',
                    '<em>', gettext('None'), '</em>',
                '</tpl>',
                '<ul class="relateduserlist">',
                    '<tpl if="users.length &gt; 0">',
                        '<tpl for="users">',
                            '<li relateduserlistitem relateduserlistitem_{data.user.username}>',
                                '{data.user.full_name}',
                            '</li>',
                        '</tpl>',
                    '</tpl>',
                '</ul>',
            '</tpl>',
            '<tpl if="loading">',
                gettext('Loading ...'),
            '</tpl>',
        '</div>'
    ],

    /**
     * @cfg {String} css_suffix
     * The suffix to add to the css class with.
     */

    /**
     * @cfg {String} title
     * The title of the list.
     */

    /**
     * @cfg {String} buttonText
     * The text of the "manage" button
     */

    /**
     * @cfg {String} managepanelxtype
     * The xtype of the manage panel.
     */
    managepanelxtype: 'managerelateduserspanel',

    initComponent: function() {
        var cls = Ext.String.format('devilry_subjectadmin_listofrelatedusers devilry_subjectadmin_listofrelated_{0}', this.css_suffix);
        Ext.apply(this, {
            layout: 'border',
            cls: cls,
            height: 200,
            items: [{
                xtype: 'panel',
                ui: 'lookslike-parawitheader-panel',
                title: this.title,
                region: 'center',
                autoScroll: true,
                items: [{
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'box',
                    itemId: 'userslist',
                    tpl: this.listTemplate,
                    data: {
                        loading: true
                    }
                }],
                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'bottom',
                    ui: 'footer',
                    items: [{
                        xtype: 'button',
                        itemId: 'manageButton',
                        scale: 'medium',
                        disabled: true,
                        text: this.buttonText,
                        listeners: {
                            scope: this,
                            click: this._onManage
                        }
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getTplData: function(extra) {
        var data = {
            title: this.title
        };
        Ext.apply(data, extra);
        return data;
    },

    setLoadedStore: function(store) {
        this.down('#userslist').update({
            users: store.data.items
        });
        this.down('#manageButton').enable();
        this.store = store;
    },

    setFailedToLoad: function(operation) {
        this.down('#userslist').update({});
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(null, operation);
        this.down('alertmessagelist').addMany(error.errormessages, 'error');
    },

    _onManage: function() {
        Ext.widget('window', {
            layout: 'fit',
            closable: true,
            width: 700,
            height: 500,
            maximizable: true,
            modal: true,
            title: this.buttonText,
            items: {
                xtype: this.managepanelxtype,
                store: this.store,
                listeners: {
                    scope: this,
                    usersAdded: function(userRecords) {
                        //this._updateView();
                    },
                    usersRemoved: function(userRecords) {
                        //this._updateView();
                    }
                }
            }
        }).show();
    }
});
