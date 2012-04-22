/**
 * A widget that shows if an assignment is published, when it was/is-to-be
 * published, and provides an edit button which a controller can use to
 * display widget to change the publishing_time.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditPublishingTimeWidget', {
    extend: 'themebase.EditableSidebarBox',
    alias: 'widget.editpublishingtime-widget',
    cls: 'editpublishingtime-widget'
});
