/**
 * Tooltip classes for Assignmentgroup.
 * 
 */
Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.AssignmentGroup', {
 
    tooltip_models: ["StaticFeedbackNext", 'StaticFeedbackPrevious',
                        'BrowseFiles', 'AboutTheDelivery',
                        'CreateNewDeadline', 'OtherDeliveries',
                        'SearchField'
                    ],
 
    prefix: 'devilry.extjshelpers.tooltips.assignmentgroup.AssignmentGroup',
 
    requires: [
        'devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext',
        'devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles'
    ],
    
    initComponent: function() { 

        this.feedback_next = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext', {});
        this.feedback_previous = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackPrevious', {});   
        //this.browse_files = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles', {});
        this.about = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.AboutTheDelivery', {});
        this.create_new_deadline = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.CreateNewDeadline', {});
        this.other_deliveries = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.OtherDeliveries', {});
        this.search_field = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.SearchField', {});
        this.warning_field = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.WarningField', {});
        this.feedback_window = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.FeedbackWindow', {});
    },
    /**
     * Animate all tooltips as a wizard.
     * 
     */    
    animateAndShowAll: function() {
        //TODO activated when HELP button in the upper right corner is pressed
        for (tooltip in this.tooltip_models) {
            console.log(this.tooltip_models[tooltip]);
        }
        console.log(this.prefix);
    },
    
    toString: function() {
        return "Hei dette er klassen sin det!";
    }

});
