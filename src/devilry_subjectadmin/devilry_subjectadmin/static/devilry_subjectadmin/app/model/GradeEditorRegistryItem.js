Ext.define('devilry_subjectadmin.model.GradeEditorRegistryItem', {
    extend: 'devilry.gradeeditors.RestfulRegistryItem',


    isConfigurable: function() {
        var config_editor_url = this.get('config_editor_url');
        return !Ext.isEmpty(config_editor_url);
    }
});
