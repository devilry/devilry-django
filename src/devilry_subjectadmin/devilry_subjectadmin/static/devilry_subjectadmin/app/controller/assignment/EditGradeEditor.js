Ext.define('devilry_subjectadmin.controller.assignment.EditGradeEditor', {
    extend: 'Ext.app.Controller',

    views: [
        'assignment.GradeEditorSelectWindow',
        'assignment.GradeEditorSelectWidget'
    ],

    controllers: [
        'assignment.Overview'
    ],

    models: ['Assignment'],

    refs: [{
        ref: 'gradeEditorSelectWindow',
        selector: 'gradeeditorselectwindow'
    }, {
        ref: 'gradeEditorSelectWidget',
        selector: 'gradeeditorselect-widget'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            assignmentSuccessfullyLoaded: this._onLoadAssignment
        });
        this.control({
            'gradeeditorselectwindow savebutton': {
                click: this._onSave
            },
            'gradeeditorselectwindow cancelbutton': {
                click: this._closeSelectWindow
            },
            'gradeeditorselect-widget': {
                edit: this._onEdit
            }
        });
    },

    _onLoadAssignment: function(assignmentRecord) {
        this.assignmentRecord = assignmentRecord;
        this.getGradeEditorSelectWidget().enable();
        this._updateWidget();
    },

    _closeSelectWindow: function() {
        this.getGradeEditorSelectWindow().close();
    },

    _onSave: function() {
    },

    _getMaskElement: function() {
        return this.getGradeEditorSelectWindow().getEl();
    },

    _onSaveSuccess: function() {
        this._getMaskElement().unmask();
        this._closeSelectWindow();
        this._updateWidget();
    },

    _onProxyError: function(proxy, response, operation) {
        this._getMaskElement().unmask();
        alert('Save error');
    },

    _onEdit: function() {
        Ext.widget('gradeeditorselectwindow').show();
    },

    _updateWidget: function() {
        console.log('update');
        //var anonymous = this.assignmentRecord.get('anonymous');
        //var title, body;

        //if(anonymous) {
            //title = gettext('Anonymous');
            //body = gettext('Examiners and students can not see each other and they can not communicate.');
        //} else {
            //title = gettext('Not anonymous');
            //body = gettext('Examiners and students can see each other and communicate.');
        //}
        //var anonymous = this.assignmentRecord.get('anonymous');
        //this.getAnonymousWidget().updateTitle(title);
        //this.getAnonymousWidget().updateText(body);
    }
});
