Ext.define('subjectadmin.controller.ChoosePeriod', {
    extend: 'Ext.app.Controller',

    views: [
        'chooseperiod.ActivePeriodsList',
        'chooseperiod.ChoosePeriod'
    ],

    stores: [
        'ActivePeriods'
    ],

    refs: [{
        ref: 'nextButton',
        selector: 'button[cls=next]'
    }, {
        ref: 'choosePeriod',
        selector: 'chooseperiod'
    }, {
        ref: 'activePeriodsList',
        selector: 'activeperiodslist'
    }],

    init: function() {
        this.control({
            'viewport activeperiodslist': {
                render: this._onRender,
                select: this._onSelectPeriod,
                deselect: this._onDeSelectPeriod
            },
            'viewport button[scale=large]': {
                click: this._onNext
            }
        });
    },

    _onRender: function() {
        this.getNextButton().disable();
    },

    _onDeSelectPeriod: function() {
        this.getNextButton().disable();
    },
    _onSelectPeriod: function() {
        this.getNextButton().enable();
    },

    _onNext: function() {
        var nexturlformat = this.getChoosePeriod().nexturlformat;
        var periodid = this.getActivePeriodsList().getSelectionModel().getLastSelected().get('id');
        var nexturl = Ext.String.format(nexturlformat, periodid);
        this.application.route.navigate(nexturl);
    }
});
