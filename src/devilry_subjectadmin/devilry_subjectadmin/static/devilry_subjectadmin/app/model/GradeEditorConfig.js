Ext.define('devilry_subjectadmin.model.GradeEditorConfig', {
    extend: 'devilry.apps.gradeeditors.simplified.administrator.SimplifiedConfig',

    hasConfig: function() {
        return !Ext.isEmpty(this.get('config'));
    }
});
