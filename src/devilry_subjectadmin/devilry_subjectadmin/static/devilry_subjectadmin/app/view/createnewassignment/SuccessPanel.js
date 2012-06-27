/**
 * Success page for CreateNewAssignment.
 */
Ext.define('devilry_subjectadmin.view.createnewassignment.SuccessPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.createnewassignment-successpanel',
    requires: [
        'devilry_subjectadmin.view.ActionList',
        'devilry_subjectadmin.utils.UrlLookup',
        'Ext.XTemplate'
    ],
    cls: 'devilry_subjectadmin_createnewassignment_successpanel',

    bodyPadding: 40,
    autoScroll: true,
    items: [{
        xtype: 'panel',
        itemId: 'body',
        title: '',
        ui: 'inset-header-strong-panel'
    }],


    /**
     * The ``config`` parameter must have the following attributes:
     *
     * periodpath (required)
     *      The path to the period where the assignment was created.
     * short_name (required)
     *      The ``short_name`` of the created assignment.
     * period_id (required)
     *      The ``id`` of the period where the assignment was created.
     * assignment_id (required)
     *      The ``id`` of the newly created assignment.
     */
    setup: function(config) {
        this.bodyPanel = this.down('#body');
        this.config = config;
        this.assignmentpath = Ext.String.format('{0}.{1}',
            config.periodpath, this.config.short_name
        );
        this._setTitle();
        this._addLinks();
    },

    _apply_template: function(tpl, data) {
        return Ext.create('Ext.XTemplate', tpl).apply(data);
    },

    _setTitle: function() {
        var title = this._apply_template(gettext('Created {assignmentpath}'), {
            assignmentpath: this.assignmentpath
        });
        this.bodyPanel.setTitle(title);
    },

    _addLinks: function() {
        var gotoText = this._apply_template(gettext('Go to {assignmentpath}'), {
            assignmentpath: this.assignmentpath
        });

        var links = [{
            url: devilry_subjectadmin.utils.UrlLookup.assignmentOverview(this.config.assignment_id),
            text: gotoText
        }, {
            url: Ext.String.format(
                '#/@@create-new-assignment/{0}',
                this.config.period_id
            ),
            buttonType: 'default',
            buttonSize: 'normal',
            text: gettext('Add another assignment')
        }]
        this.bodyPanel.add({
            xtype: 'actionlist',
            width: 460,
            linkStyle: 'width: 100%',
            links: links
        });
    }
});
