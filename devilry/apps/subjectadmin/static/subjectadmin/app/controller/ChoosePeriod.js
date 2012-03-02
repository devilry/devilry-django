Ext.define('subjectadmin.controller.ChoosePeriod', {
    extend: 'Ext.app.Controller',

    //requires: [
        //'themebase.NextButton',
    //],
    //views: [
        //'ActivePeriodsList',
        //'createnewassignment.ChoosePeriod'
    //],

    //stores: [
        //'ActivePeriods'
    //],

    //refs: [{
        //ref: 'nextFromPageOneButton',
        //selector: 'chooseperiod nextbutton'
    //}, {
        //ref: 'choosePeriod',
        //selector: 'chooseperiod'
    //}, {
        //ref: 'activePeriodsList',
        //selector: 'chooseperiod activeperiodslist'
    //}],

    init: function() {
        console.log('chooseperiod');
        //this.getActivePeriodsStore().load();
        //this.control({
            //'viewport chooseperiod activeperiodslist': {
                //render: this._onRenderActivePeriodlist,
                //select: this._onSelectPeriod,
                //deselect: this._onDeSelectPeriod
            //},
            //'viewport chooseperiod nextbutton': {
                //click: this._onNextFromPageOne
            //}
        //});
    },

    //_onRenderActivePeriodlist: function() {
        //this.getNextFromPageOneButton().disable();
    //},

    //_onDeSelectPeriod: function() {
        //this.getNextFromPageOneButton().disable();
    //},
    //_onSelectPeriod: function() {
        //this.getNextFromPageOneButton().enable();
    //},

    //_onNextFromPageOne: function() {
        //var nexturlformat = '/@@create-new-assignment/{0}';
        //var periodid = this.getActivePeriodsList().getSelectionModel().getLastSelected().get('id');
        //var nexturl = Ext.String.format(nexturlformat, periodid);
        //this.application.route.navigate(nexturl);
    //}
});
