/**
 * Success page for CreateNewAssignment.
 */
Ext.define('subjectadmin.view.createnewassignment.SuccessPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.createnewassignment-successpanel',
    requires: [
        'subjectadmin.view.ActionList'
    ],
    cls: 'createnewassignment-successpanel',

    bodyPadding: 20,
    autoScroll: true,
    items: [{
        xtype: 'box',
        itemId: 'header'
    }],

    headertemplate: [
        '<h2>{success}</h2>',
        '<p>{message}</p>'
    ],


    initComponent: function() {
        this.callParent(arguments);
    },

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
        var header = Ext.create('Ext.XTemplate', this.headertemplate).apply({
            success: dtranslate('themebase.success'),
            message: dtranslate('subjectadmin.createnewassignment.success.message')
        });
        this.down('#header').update(header);

        var links = [{
            url: Ext.String.format(
                '#/{0}/{1}/{2}',
                config.subject_short_name,
                config.period_short_name,
                config.short_name
            ),
            text: dtranslate('subjectadmin.createnewassignment.success.gotocreated')
        }, {
            url: '#/@@create-new-assignment/@@chooseperiod',
            buttonType: 'default',
            text: dtranslate('subjectadmin.createnewassignment.success.addanother')
        }, {
            url: Ext.String.format(
                '#/@@create-new-assignment/{0},{1}',
                config.period_id, config.delivery_types
            ),
            buttonType: 'default',
            text: dtranslate('subjectadmin.createnewassignment.success.addanother-similar')
        }]
        this.add({
            xtype: 'actionlist',
            links: links
        });
    }
});
