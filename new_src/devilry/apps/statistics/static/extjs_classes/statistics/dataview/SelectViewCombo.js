Ext.define('devilry.statistics.dataview.SelectViewCombo', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.statistics-dataview-selectviewcombo',
    valueField: 'clsname',
    displayField: 'label',
    forceSelection: true,
    editable: false,
    
    config: {
        availableViews: [],
        defaultViewClsname: undefined
    },
    
    constructor: function(config) {
        this.addEvents('selectView');
        this.initConfig(config);
        this.callParent([config]);
    },
    
    initComponent: function() {
        var selectViewStore = Ext.create('Ext.data.Store', {
            fields: ['clsname', 'label'],
            data: this.availableViews,
            proxy: 'memory'
        });
        Ext.apply(this, {
            store: selectViewStore,
            emptyText: this._findDefaultViewInAvailableViews().label
        });
        this.on('select', this._onSelectView, this);
        this.callParent(arguments);
    },

    _findDefaultViewInAvailableViews: function() {
        var view;
        Ext.each(this.availableViews, function(availableView, index) {
            if(availableView.clsname === this.defaultViewClsname) {
                view = availableView;
                return false; // break
            }
        }, this);
        return view;
    },

    _onSelectView: function(combo, records) {
        var record = records[0];
        this.fireEvent('selectView', record.get('clsname'));
    }
});
