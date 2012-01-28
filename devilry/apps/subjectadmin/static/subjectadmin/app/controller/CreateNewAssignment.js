Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    views: [
        'createnewassignment.Form',
        'createnewassignment.CreateNewAssignment'
    ],

    refs: [{
        ref: 'form',
        selector: 'createnewassignmentform'
    }, {
        ref: 'createNewAssignment',
        selector: 'createnewassignment'
    }],

    init: function() {
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderForm,
            },
            'viewport createnewassignmentform primarybutton': {
                click: this._onSubmit,
            }
        });
    },

    _onRenderForm: function(form) {
        form.keyNav = Ext.create('Ext.util.KeyNav', form.el, {
            enter: this._onSubmit,
            scope: this
        });
    },

    _onSubmit: function() {
        var form = this.getForm().getForm();
        if(form.isValid()) {
            var values = form.getFieldValues();
            this._save(values);
        }
    },

    _save: function(values) {
        var periodId = this.getCreateNewAssignment().periodId;
        values.parentnode = periodId;
        console.log('save', values);
    },

    _sendRestRequest: function(args) {
        Ext.apply(args, {
            url: Ext.String.format(),
        });
        Ext.Ajax.request(args);
    }
});
