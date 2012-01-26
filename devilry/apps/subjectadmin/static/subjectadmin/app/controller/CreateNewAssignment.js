Ext.define('subjectadmin.controller.CreateNewAssignment', {
    extend: 'Ext.app.Controller',

    views: [
        'createnewassignment.Form',
        'createnewassignment.ActivePeriodsList'
    ],

    stores: [
        'ActivePeriods'
    ],

    refs: [{
        ref: 'form',
        selector: 'createnewassignmentform'
    }, {
        ref: 'activePeriodsList',
        selector: 'activeperiodslist'
    }],

    init: function() {
        this.control({
            'viewport createnewassignmentform': {
                render: this._onRenderForm
            }
        });
    },

    _onRenderForm: function() {
        this.getActivePeriodsStore().load({
            scope: this,
            callback: this._onLoadActivePeriods
        });
    },

    _onLoadActivePeriods: function() {
        if(this.getActivePeriodsStore().getTotalCount() > 0) {
            //this._selectFirstPeriod();
        }
    },

    /** Work arount timing issues by re-trying to select the first item in the
     * activeperiodslist until it does not throw an exception. */
    _selectFirstPeriod: function() {
        var selectionmodel = this.getActivePeriodsList().getSelectionModel();
        try {
            selectionmodel.select(0);
        } catch(error) {
            Ext.defer(this._selectFirstPeriod, 200, this);
        }
    }
});
