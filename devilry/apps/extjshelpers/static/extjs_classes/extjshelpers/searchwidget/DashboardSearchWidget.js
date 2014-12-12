Ext.define('devilry.extjshelpers.searchwidget.DashboardSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],
    mixins: {
        comboBoxTemplates: 'devilry.extjshelpers.ComboboxTemplatesMixin'
    },

    _createStore: function(modelname) {
        var model = Ext.ModelManager.getModel(modelname);
        var store = Ext.create('Ext.data.Store', {
            model: model,
            remoteFilter: true,
            remoteSort: true,
            proxy: model.proxy.copy()
        });
        return store;
    }
});
