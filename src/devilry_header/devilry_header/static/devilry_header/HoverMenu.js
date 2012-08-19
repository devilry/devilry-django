Ext.define('devilry_header.HoverMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_hovermenu',
    cls: 'devilryheader_hovermenu',
    floating: true,
    frame: false,
    border: 0,
    //autoShow: true,
    autoScroll: true,
    topOffset: 30,

    requires: [
        'devilry_header.Roles',
        'devilry_header.HelpLinksBox',
        'devilry_header.UserInfoBox',
        'devilry_i18n.LanguageSelectWidget'
    ],

    initComponent: function() {
        this._setupAutosizing();

        Ext.apply(this, {
            layout: 'column',
            items: [{
                width: 300,
                xtype: 'container',
                padding: '10 20 10 10',
                items: [{
                    xtype: 'box',
                    html: [
                        '<h2>',
                            gettext('Choose your role'),
                        '</h2>'
                    ].join('')
                }, {
                    xtype: 'devilryheader_roles'
                }]
            }, {
                columnWidth: 1.0,
                padding: '10 10 10 20',
                xtype: 'container',
                items: [{
                    xtype: 'devilryheader_userinfobox'
                }, {
                    xtype: 'container',
                    margin: '30 0 0 0',
                    items: [{
                        xtype: 'box',
                        html: ['<h2>', gettext('Language'), '</h2>'].join('')
                    }, {
                        xtype: 'devilry_i18n_languageselect',
                        width: 250
                    }]

                }, {
                    margin: '30 0 0 0',
                    xtype: 'devilryheader_helplinksbox'
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getRoles: function() {
        return this.down('devilryheader_roles');
    },
    _getUserInfoBox: function() {
        return this.down('devilryheader_userinfobox');
    },
    _getHelpLinksBox: function() {
        return this.down('devilryheader_helplinksbox');
    },

    setUserInfoRecord: function(userInfoRecord) {
        this._getRoles().setUserInfoRecord(userInfoRecord);
        this._getUserInfoBox().setUserInfoRecord(userInfoRecord);
        this._getHelpLinksBox().setUserInfoRecord(userInfoRecord);
    },


    //
    //
    // Autoresize to window size
    //
    //

    _setupAutosizing: function() {
       // Get the DOM disruption over with before the component renders and begins a layout
        Ext.getScrollbarSize();
        
        // Clear any dimensions, we will size later on
        this.width = this.height = undefined;

        Ext.fly(window).on('resize', this._onWindowResize, this);
        this.on('show', this._onShow, this);
    },

    _onWindowResize: function() {
        if(this.isVisible()) {
            this._setSizeAndPosition();
        }
    },

    _setSizeAndPosition: function() {
        var bodysize = Ext.getBody().getViewSize();
        this.setSize({
            width: bodysize.width,
            height: bodysize.height - this.topOffset
        });
        this.setPagePosition(0, this.topOffset);
    },

    _onShow: function() {
        this._setSizeAndPosition();
    }
});
