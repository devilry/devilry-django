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
                render: this._onRenderForm,
            }
        });
    },

    _onRenderForm: function(form) {
        form.keyNav = Ext.create('Ext.util.KeyNav', form.el, {
            enter: this._onEnterKey,
            scope: this
        });
    },

    _onEnterKey: function() {
        var form = this.getForm().getForm();
        if(form.isValid()) {
            var values = form.getFieldValues();
            console.log(values);
        }
    }
});
