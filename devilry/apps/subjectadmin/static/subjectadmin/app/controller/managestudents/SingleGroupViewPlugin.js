/**
 * Controller that handles tasks when a single group is selected.
 *
 */
Ext.define('subjectadmin.controller.managestudents.SingleGroupView', {
    extend: 'Ext.app.Controller',

    views: [
        'managestudents.Overview',
        'managestudents.ListOfGroups'
    ],


    refs: [{
        ref: 'overview',
        selector: 'managestudentsoverview'
    //}, {
        //ref: 'listOfGroups',
        //selector: 'listofgroups'
    }, {
        ref: 'body',
        selector: 'managestudentsoverview #body'
    }, {
        ref: 'listofgroupsToolbar',
        selector: 'managestudentsoverview toolbar[itemId=listofgroupsToolbar]'
    }],

    init: function() {
        this.control({
            'viewport managestudentsoverview': {
                render: this._onRender
            },
            'viewport managestudentsoverview listofgroups': {
                selectionchange: this._onGroupSelectionChange
            }
        });
    },

    _onRender: function() {
        this.subject_shortname = this.getOverview().subject_shortname;
        this.period_shortname = this.getOverview().period_shortname;
        this.assignment_shortname = this.getOverview().assignment_shortname;
        //this.getOverview().getEl().mask(dtranslate('themebase.loading'));
        this.loadAssignment();
    }
});
