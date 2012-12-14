Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.BulkManageDeadlinesPanel' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.bulkmanagedeadlinespanel', // Define the widget xtype as allwhereisadminpanel
    cls: 'devilry_subjectadmin_bulkmanagedeadlinespanel',

    requires: [
        'devilry_extjsextras.AlertMessageList',
        'devilry_subjectadmin.view.bulkmanagedeadlines.CreateDeadlineForm',
        'devilry_extjsextras.PrimaryButton'
    ],

    /**
     * @cfg {int} [assignment_id]
     * The ID of the assignment to load deadlines for.
     */

    /**
     * @cfg {string} [bulkdeadline_id=undefined]
     * The deadline to open on load.
     */

    /**
     * @cfg {bool} [edit_deadline=false]
     * Edit the deadline specified by ``bulkdeadline_id`` on load?
     */

    /**
     * @cfg {bool} [add_deadline=false]
     * Add a deadline on load?
     */

    frame: false,
    border: 0,
    padding: 20,
    autoScroll: true, // Autoscroll on overflow


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'alertmessagelist',
                itemId: 'globalAlertmessagelist'
            }, {
                xtype: 'container',
                itemId: 'addDeadlineBodyContainer',
                hidden: true,
                items: [{
                    xtype: 'container',
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: [
                            '<h1>',
                                gettext('Add deadline'),
                            '</h1>'
                        ].join('')
                    }, {
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: [
                            '<p class="muted">',
                                gettext('Students are in a group even if they work alone. Each group has their own individual deadlines. Use the form below to add a deadline to many groups.'),
                            '</p>'
                        ].join('')
                    }]
                }, {
                    xtype: 'bulkmanagedeadlines_createdeadlineform',
                    assignment_id: this.assignment_id,
                    saveButtonDisabled: true,
                    margin: '20 0 0 0'
                }]
            }, {
                xtype: 'container',
                itemId: 'normalBodyContainer',
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: [
                        '<h1>',
                            gettext('Deadlines'),
                        '</h1>'
                    ].join('')
                }, {
                    xtype: 'container',
                    layout: 'column',
                    margin: '0 0 20 0',
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap',
                        columnWidth: 1,
                        margin: '0 40 0 0',
                        html: [
                            '<p class="muted">',
                                gettext('Students are in a group even if they work alone. Each group has their own individual deadlines. In this view, we have grouped deadlines with exactly the same date/time and text to make it easy for you to change them in bulk.'),
                            '</p>'
                        ].join('')
                    }, {
                        xtype: 'button',
                        itemId: 'addDeadlineButton',
                        scale: 'large',
                        cls: 'add_deadline_button',
                        width: 220,
                        text: gettext('Add deadline')
                    }]
                }, {
                    xtype: 'panel',
                    frame: false,
                    style: 'background-color: transparent !important',
                    bodyStyle: 'background-color: transparent !important',
                    itemId: 'deadlinesContainer',
                    layout: 'anchor',
                    defaults: {
                        anchor: '100%'
                    },
                    cls: 'devilry_discussionview_container'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
