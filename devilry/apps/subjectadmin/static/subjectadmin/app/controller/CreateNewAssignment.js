Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    views: [
        'createnewassignment.Form',
        'createnewassignment.CreateNewAssignment'
    ],

    refs: [{
        ref: 'form',
        selector: 'createnewassignmentform'
    }],

    init: function() {
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderForm
            }
        });
    },

    _onRenderForm: function() {
    }
});
