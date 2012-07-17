/**
 * Overview of relatated users on a period.
 */
Ext.define('devilry_subjectadmin.view.period.ListOfRelatedUsers' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.listofrelatedusers',
    requires: [
        'devilry_extjsextras.AlertMessageList',
        'devilry_extjsextras.DjangoRestframeworkProxyErrorHandler'
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
                        text: this.buttonText
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

    setUserRecords: function(records) {
        this.down('#userslist').update({
            users: records
        });
        this.down('button').enable();
    },

    setFailedToLoad: function(operation) {
        this.down('#userslist').update({});
        var error = Ext.create('devilry_extjsextras.DjangoRestframeworkProxyErrorHandler', operation);
        error.addErrors(null, operation);
        this.down('alertmessagelist').addMany(error.errormessages, 'error');
    }
});
