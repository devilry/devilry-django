Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.EditDeadlineForm', {
    extend: 'devilry_subjectadmin.view.bulkmanagedeadlines.BaseDeadlineForm',
    alias: 'widget.bulkmanagedeadlines_editdeadlineform',
    extraCls: 'editdeadlineform',

    getItems: function() {
        var items = this.callParent();
        return items;
    }
});
