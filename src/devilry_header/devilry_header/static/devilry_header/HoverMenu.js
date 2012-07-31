Ext.define('devilry_header.HoverMenu', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader_hovermenu',
    cls: 'devilryheader_hovermenu',
    floating: true,
    frame: false,
    border: 0,
    autoShow: true,
    autoScroll: true,

    requires: [
        'devilry_header.Roles'
    ],

    initComponent: function() {
        this._setupAutosizing();

        Ext.apply(this, {
            items: [{
                xtype: 'devilryheader_roles',
                padding: 10
            }]
        });
        this.callParent(arguments);
    },

    _getRoles: function() {
        return this.down('devilryheader_roles');
    },

    setUserInfoRecord: function(userInfoRecord) {
        this._getRoles().setUserInfoRecord(userInfoRecord);
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

        Ext.fly(window).on('resize', this._setSizeAndPosition, this);
        this.on('show', this._onShow, this);
    },

    _setSizeAndPosition: function() {
        this.setSize(Ext.getBody().getViewSize());
        this.setPagePosition(0, 30);
    },

    _onShow: function() {
        this._setSizeAndPosition();
    },
});
