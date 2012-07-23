Ext.define('devilry_subjectadmin.view.addgroups.Overview', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.addgroupsoverview',
    cls: 'devilry_subjectadmin_addstudentsoverview',
    requires: [
    ],

    /**
     * @cfg {Object} [assignment_id] (required)
     */

    /**
     * @cfg {String} [on_save_success_url] (required)
     */

    /**
     * @cfg {String} [breadcrumbtype] (required)
     * See controller.AddGroups._setBreadcrumb
     */

    layout: 'fit',
    title: gettext('Choose from students registered on the period'),

    setBody: function(config) {
        this.removeAll();
        this.add(config);
    }
});
