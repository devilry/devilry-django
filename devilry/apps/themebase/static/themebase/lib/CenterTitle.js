Ext.define('themebase.CenterTitle', {
    extend: 'Ext.Component',
    alias: 'widget.centertitle',

    /**
     * @cfg {String} title
     */

    tpl: ['<h2 class="centertitle">{title}</h2>'],

    initComponent: function() {
        this.data = {
            title: this.title
        };
        this.callParent(arguments);
    },

    update: function(title) {
        this.callParent({
            title: title
        });
    }
});
