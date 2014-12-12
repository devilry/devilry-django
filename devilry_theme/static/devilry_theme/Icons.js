/** Singleton instance with attributes with properties for icon urls. */
Ext.define('devilry_theme.Icons', {
    singleton: true,

    small: [
        /**
         * @property DELETE_SMALL
         * 16x16 delete icon.
         */
        'delete',

        /**
         * @property ADD_SMALL
         * 16x16 add icon.
         */
        'add',

        /**
         * @property HELP_SMALL
         * 16x16 help icon.
         */
        'help'
    ],

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);

        this._addIcons(this.small, '16x16', '_SMALL');
    },

    _addIcons: function(icons, folder, suffix) {
        Ext.Array.each(icons, function(name) {
            var attrname = name.toUpperCase() + suffix;
            this[attrname] = this._getIconUrl(folder, name);
        }, this);
    },

    _getIconUrl: function(folder, name) {
        return DevilrySettings.DEVILRY_STATIC_URL +
            Ext.String.format('/devilry_theme/resources/icons/{0}/{1}.png',
                folder, name);
    }
});
