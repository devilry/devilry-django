Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    views: [
        'createnewassignment.Form',
        'createnewassignment.CreateNewAssignment'
    ],

    stores: [
        'ActiveAssignments'
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
            'viewport createnewassignmentform textfield[name=long_name]': {
                render: this._onRenderLongName,
            },
            'viewport createnewassignmentform primarybutton': {
                click: this._onSubmit,
            }
        });
    },

    _onRenderLongName: function(field) {
        field.focus();
    },

    _onRenderForm: function() {
        this.getForm().keyNav = Ext.create('Ext.util.KeyNav', this.getForm().el, {
            enter: this._onSubmit,
            scope: this
        });
        this._setInitialValues();
    },

    _setInitialValues: function() {
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
        var store = this.getActiveAssignmentsStore();
        this.mon(store, 'datachanged', this._onStoreDataChanged, this, {
            single: true
        });
        store.add(values);
        store.sync();
    },

    _onStoreDataChanged: function() {
        console.log(this.getActiveAssignmentsStore().data.items);
    }
});
