/**
 * Success page for CreateNewAssignment.
 */
Ext.define('devilry_subjectadmin.view.createnewassignment.SuccessPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.createnewassignment-successpanel',
    requires: [
        'devilry_subjectadmin.view.ActionList',
        'Ext.XTemplate'
    ],
    cls: 'createnewassignment-successpanel',

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
     * subject_short_name (required)
     *      The ``short_name`` of the subject where the assignment was created.
     * period_short_name (required)
     *      The ``short_name`` of the period where the assignment was created.
     * short_name (required)
     *      The ``short_name`` of the created assignment.
     * period_id (required)
     *      The ``id`` of the period where the assignment was created.
     */
    setup: function(config) {
        this.bodyPanel = this.down('#body');
        this.config = config;
        this.period = Ext.String.format('{0}.{1}',
            this.config.subject_short_name, this.config.period_short_name
        );
        this.assignment = Ext.String.format('{0}.{1}',
            this.period, this.config.short_name
        );
        this._setTitle();
        this._addLinks();
    },

    _setTitle: function() {
        var title = Ext.create('Ext.XTemplate', dtranslate('devilry_subjectadmin.createnewassignment.success.title')).apply({
            assignment: this.assignment
        });
        this.bodyPanel.setTitle(title);
    },

    _addLinks: function() {
        var gotoText = Ext.create('Ext.XTemplate', dtranslate('devilry_subjectadmin.createnewassignment.success.gotocreated')).apply({
            assignment: this.assignment
        });

        var links = [{
            url: Ext.String.format(
                '#/{0}/{1}/{2}/',
                this.config.subject_short_name,
                this.config.period_short_name,
                this.config.short_name
            ),
            text: gotoText
        }, {
            url: Ext.String.format(
                '#/@@create-new-assignment/{0}',
                this.config.period_id
            ),
            buttonType: 'default',
            buttonSize: 'normal',
            text: dtranslate('devilry_subjectadmin.createnewassignment.success.addanother')
        }]
        this.bodyPanel.add({
            xtype: 'actionlist',
            width: 460,
            linkStyle: 'width: 100%',
            links: links
        });
    }
});
