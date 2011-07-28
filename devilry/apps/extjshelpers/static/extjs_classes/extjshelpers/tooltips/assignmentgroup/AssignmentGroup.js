/**
 * Tooltip classes for Assignmentgroup.
 * 
 */
Ext.define('devilry.extjshelpers.tooltips.assignmentgroup.ToolTip', {
 
    tooltip_models: ['StaticFeedbackNext', 'StaticFeedbackPrevious',
                        'BrowseFiles', 'AboutTheDelivery',
                        'CreateNewDeadline', 'OtherDeliveries',
                        'SearchField'
                    ],
 
     /**
     * Tooltip for next button
     * 
     */
    feedback_next: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackNext', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to get to the next feedback'
    });
    
    /**
     * Tooltip for previous button
     * 
     */
    feedback_previous: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.StaticFeedbackPrevious', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to get to the previous feedback'
    });
    
    /**
     * Tooltip for browse files button
     * 
     */
    browse_files: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.BrowseFiles', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to view the files in this delivery'
    });
    
    /**
     * Tooltip for About button
     * 
     */
    about: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.AboutTheDelivery', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to get more info about the delivery'
    });
    
    /**
     * Tooltip for create new deadline button
     * 
     */
    create_new_deadline: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.CreateNewDeadline', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to create a new deadline for deliveries'
    });
    
    /**
     * Tooltip for other deliveries button
     * 
     */
    other_deliveries: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.OtherDeliveries', {
        extend: 'Ext.tip.ToolTip',
        html: 'Click to view this groups other deliveries'
    });
    
    /**
     * Tooltip for the search field
     * 
     */
    search_field: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.SearchField', {
        extend: 'Ext.tip.ToolTip',
        html: 'Search within this assignment'
    });
    
    /**
     * Tooltip for the warning field
     * 
     */
    warning_field: Ext.create('devilry.extjshelpers.tooltips.assignmentgroup.WarningField', {
        extend: 'Ext.tip.ToolTip',
        html: 'Information about the current delivery'
    });
    
    /**
     * Animate all tooltips as a wizard.
     * 
     */    
    animateAndShowAll: function() {
        //TODO activated when HELP button in the upper right corner is pressed
        for (tooltip in this.tooltip_models) {
            console.log(tooltip);
        }
    };

});