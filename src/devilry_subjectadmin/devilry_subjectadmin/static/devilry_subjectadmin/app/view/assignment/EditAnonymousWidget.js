/**
 * A widget that shows if an assignment is anonymous, and provides an edit
 * button which a controller can use to handle changing the attribute.
 * */
Ext.define('devilry_subjectadmin.view.assignment.EditAnonymousWidget', {
    extend: 'devilry_extjsextras.EditableSidebarBox',
    alias: 'widget.editanonymous-widget',
    cls: 'devilry_subjectadmin_editanonymous_widget',
    bodyTpl: '<p class="muted">{text}</p>'
});
