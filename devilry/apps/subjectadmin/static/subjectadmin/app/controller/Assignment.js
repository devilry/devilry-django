/**
 * Controller for the assignment overview.
 */
Ext.define('subjectadmin.controller.Assignment', {
    extend: 'Ext.app.Controller',

    //requires: [
    //],
    views: [
        'assignment.Assignment',
        'ActionList'
    ],

    //stores: [
    //],
    //models: [
    //],

    refs: [{
        ref: 'gradeEditorSidebarBox',
        selector: 'editablesidebarbox[itemId=gradeeditor]'
    }, {
        ref: 'publishingTimeSidebarBox',
        selector: 'editablesidebarbox[itemId=publishingtime]'
    }],

    init: function() {
        this.control({
            'viewport assignment editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport assignment editablesidebarbox[itemId=publishingtime] button': {
                click: this._onEditPublishingTime
            }
        });
    },

    _onEditGradeEditor: function() {
        console.log('grade', this.getGradeEditorSidebarBox());
    },

    _onEditPublishingTime: function() {
        console.log('pub', this.getPublishingTimeSidebarBox());
    },
});
