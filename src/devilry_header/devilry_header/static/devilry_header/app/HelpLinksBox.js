Ext.define('devilry_header.HelpLinksBox', {
    extend: 'Ext.Component',
    alias: 'widget.devilryheader_helplinksbox',
    cls: 'devilryheader_helplinksbox',

    requires: [
        'devilry_header.HelpLinksStore'
    ],

    tpl: [
        '<h2>',
            gettext('Help'),
        '</h2>',
        '<tpl if="loading">',
            '<p>', gettext('Loading'), ' ...</p>',
        '<tpl elseif="error">',
            '<p class="error">',
                gettext('Failed to load help links. Try reloading the page.'),
            '</p>',
        '<tpl else>',
            '<tpl if="helpLinkRecords.length == 0">',
                gettext('Your local Devilry system administrator(s) have not added any external help for you. If you feel anything in Devilry is unclear, contact your local Devilry system administrator(s) and ask them to add help links.'),
            '</tpl>',
            '<ul class="helplinks">',
                '<tpl for="helpLinkRecords">',
                    '<li>',
                        '<div class="title"><a href="{data.help_url}">{data.title}</a></div>',
                        '<div class="description">{data.description}</div>',
                    '</li>',
                '</tpl>',
            '</ul>',
            '<tpl if="is_superuser">',
                '<p><a class="edit_helplinks" href="{edit_helplinks_url}">',
                    gettext('Edit help links'),
                '</a></p>',
            '</tpl>',
        '</tpl>'
    ],

    data: {
        loading: true
    },


    /**
     * Set UserInfo record and update view.
     */
    setUserInfoRecord: function(userInfoRecord) {
        this.userInfoRecord = userInfoRecord;
        this.store = Ext.create('devilry_header.HelpLinksStore');
        this.store.load({
            scope: this,
            callback: this._onLoadStore
        });
    },

    _onLoadStore: function(records, operation) {
        if(operation.success) {
            this._onLoadStoreSuccess();
        } else {
            this._onLoadStoreFailure();
        }
    },

    _onLoadStoreSuccess: function() {
        var helpLinkRecords = this.store.getHelpLinksForUser(this.userInfoRecord);
        this.update({
            helpLinkRecords: helpLinkRecords,
            is_superuser: this.userInfoRecord.get('is_superuser'),
            edit_helplinks_url: DevilrySettings.DEVILRY_SUPERUSERPANEL_URL + 'devilry_helplinks/helplink/'
        });
    },

    _onLoadStoreFailure: function() {
        this.update({
            error: true
        });
    }
});
