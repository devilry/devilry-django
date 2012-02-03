/**
 * A widget that shows if an assignment is published, when it
 * was/is-to-be published, and provides a button to open a EditPublishingTime
 * window to change the publishing_time.
 * */
Ext.define('subjectadmin.view.assignment.EditPublishingTimeWidget', {
    extend: 'themebase.EditableSidebarBox',
    alias: 'widget.editpublishingtime-widget',
    cls: 'editpublishingtime-widget'
});
