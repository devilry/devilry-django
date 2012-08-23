Ext.define('devilry_subjectadmin.view.bulkmanagedeadlines.BulkManageDeadlinesPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.bulkmanagedeadlinespanel', // Define the widget xtype as allwhereisadminpanel
    cls: 'devilry_subjectadmin_bulkmanagedeadlinespanel',

    requires: [
        'devilry_extjsextras.AlertMessageList',
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
    bodyPadding: 40,
    autoScroll: true, // Autoscroll on overflow


    initComponent: function() {
        Ext.apply(this, {
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
                                interpolate(gettext('Add %(deadline_term)s'), {
                                    deadline_term: gettext('deadline')
                                }, true),
                            '</h1>'
                        ].join('')
                    }, {
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: [
                            '<p class="muted">',
                                interpolate(gettext('%(Students_term)s are in a %(group_term)s even if they work alone. Each %(group_term)s has their own individual %(deadlines_term)s. Use the form below to add a deadline to many %(groups_term)s.'), {
                                    Students_term: gettext('Students'),
                                    deadlines_term: gettext('deadlines'),
                                    group_term: gettext('group'),
                                    groups_term: gettext('groups')
                                }, true),
                            '</p>'
                        ].join('')
                    }]
                }, {
                    xtype: 'bulkmanagedeadlines_deadlineform',
                    itemId: 'addDeadlineForm',
                    assignment_id: this.assignment_id,
                    margin: '20 0 0 0'
                }]
            }, {
                xtype: 'container',
                itemId: 'normalBodyContainer',
                items: [{
                    xtype: 'box',
                    cls: 'bootstrap',
                    html: [
                        '<h1>',
                            interpolate(gettext('Manage %(deadlines_term)s'), {
                                deadlines_term: gettext('deadlines')
                            }, true),
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
                        xtype: 'primarybutton',
                        itemId: 'addDeadlineButton',
                        width: 150,
                        text: interpolate(gettext('Add %(deadline_term)s'), {
                            deadline_term: gettext('deadline')
                        }, true)
                    }]
                }, {
                    xtype: 'panel',
                    //autoScroll: true,
                    itemId: 'deadlinesContainer',
                    cls: 'devilry_discussionview_container'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
