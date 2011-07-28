/**
 * Tooltip classes for Assignmentgroup.
 * 
 */
Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.ToolTip', {
 
     /**
     * Tooltip for next button
     * 
     */
    var feedback_next = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to get to the next feedback'
    });
    
    /**
     * Tooltip for previous button
     * 
     */
    var feedback_previous = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackPrevious', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to get to the previous feedback'
    });
    
    /**
     * Tooltip for browse files button
     * 
     */
    var browse_files = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to view the files in this delivery'
    });
    
    /**
     * Tooltip for About button
     * 
     */
    var about = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.AboutTheDelivery', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to get more info about the delivery'
    });
    
    /**
     * Tooltip for create new deadline button
     * 
     */
    var create_new_deadline = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.CreateNewDeadline', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to create a new deadline for deliveries'
    });
    
    /**
     * Tooltip for other deliveries button
     * 
     */
    var other_deliveries = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.OtherDeliveries', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to view this groups other deliveries'
    });
    
    /**
     * Tooltip for the search field
     * 
     */
    var search_field = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.SearchField', {
        extend: 'Ext.tip.ToolTip',
        html: 'Search within this assignment'
    });
    
    /**
     * Tooltip for the warning field
     * 
     */
    var warning_field = Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.WarningField', {
        extend: 'Ext.tip.ToolTip',
        html: 'Information about the current delivery'
    });
    
    /**
     * Animate all tooltips as a wizard.
     * 
     */    
    animateAndShowAll: function() {
        //TODO activated when HELP button in the upper right corner is pressed
        console.log("Traverse all tool tip and show");
    };

});