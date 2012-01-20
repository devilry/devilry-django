Ext.define('devilry.extjshelpers.searchwidget.DashboardSearchWidget', {
    extend: 'devilry.extjshelpers.searchwidget.SearchWidget',
    requires: [
        'devilry.extjshelpers.searchwidget.FilterConfigDefaults',
    ],
    mixins: {
        comboBoxTemplates: 'devilry.extjshelpers.ComboboxTemplatesMixin'
    }
});
