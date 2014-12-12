Ext.define('devilry.extjshelpers.assignmentgroup.DeadlineExpiredNoDeliveriesBox', {
    extend: 'Ext.Component',
    alias: 'widget.deadlineExpiredNoDeliveriesBox',
    cls: 'widget-deadlineExpiredNoDeliveriesBox bootstrap',

    html: [
        '<div class="alert">',
            '<h3>',
                gettext('Deadline expired - no deliveries'),
            '</h3>',
            '<p>',
                gettext('The active deadline of this group has expired, and they have not made any deliveries. What would you like to do?'),
            '</p>',
            '<p>',
                '<a class="btn btn-primary btn-large createnewdeadline">',
                    '<i class="icon-time icon-white"></i> ',
                    gettext('Add a new deadline'),
                '</a> ',
                '<a class="btn btn-large closegroup">',
                    '<i class="icon-folder-close"></i> ',
                    gettext('Close the group'),
                '</a>',
            '</p>',
            '<p><small>',
                gettext('Closing the group fails the student on this assignment. You can re-open the group at any time.'),
            '</small></p>',
        '</div>'
    ].join(''),


    initComponent:function () {
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.closegroup',
            click: this._onCloseGroup
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.createnewdeadline',
            click: this._onAddDeadline
        });
        this.callParent(arguments);
    },

    _onCloseGroup:function () {
        this.fireEvent('closeGroup');
    },

    _onAddDeadline:function () {
        this.fireEvent('addDeadline');
    }
});