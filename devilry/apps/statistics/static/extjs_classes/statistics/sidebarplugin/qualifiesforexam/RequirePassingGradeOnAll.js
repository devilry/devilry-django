Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.RequirePassingGradeOnAll', {
    extend: 'Ext.button.Button',
    text: 'Apply to all students',
    iconCls: 'icon-save-32',
    scale: 'large',
    //height: 30,
    //width: 200,

    config: {
        loader: undefined,
        aggregatedStore: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            listeners: {
                scope: this,
                click: this._onClick
            }
        });
        this.callParent(arguments);
    },

    _onClick: function() {
        console.log(this.aggregatedStore);
    }
});
