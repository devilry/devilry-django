Ext.define('devilry_student.view.groupinfo.GroupMetadata' ,{
    extend: 'Ext.Component',
    alias: 'widget.groupmetadata',
    cls: 'bootstrap devilry_student_groupmetadata',

    tpl: [
        '<tpl if="groupinfo.name">',
            '<h3>', gettext('Group name'), '</h3>',
            '<p>{groupinfo.name}</p>',
        '</tpl>',

        '<tpl if="groupinfo.candidates.length &gt; 1">',
            '<h3>', gettext('Students'), '</h3>',
            '<ul>',
            '<tpl for="groupinfo.candidates">',
                '<li>',
                    '<a href="mailto:{user.email}">',
                        '{user.displayname}',
                    '</a>',
                '</li>',
            '</tpl>',
            '</ul>',
        '</tpl>',

        '<h3>', gettext('Grade'), '</h3>',
        '<p>',
            '<tpl if="groupinfo.active_feedback == null">',
                '<small>', gettext('No feedback'), '</small>',
            '<tpl else>',
                '<tpl if="groupinfo.active_feedback.feedback.is_passing_grade">',
                    '<span class="success">', gettext('Passed') ,'</span>',
                '<tpl else>',
                    '<span class="danger">', gettext('Failed') ,'</span>',
                '</tpl>',
                ' <small>({groupinfo.active_feedback.feedback.grade})</small>',
                ' - <a class="active_feedback_link" href="#/group/{groupinfo.id}/{groupinfo.active_feedback.delivery_id}">', gettext('Details'), '</a>',
            '</tpl>',
        '</p>',

        '<h3>', gettext('Status'), '</h3>',
        '<p>',
            '<tpl if="groupinfo.is_open">',
                '<span class="label label-success">', gettext('Open'), '</span> ',
                gettext('You can add more deliveries.'),
            '<tpl else>',
                '<span class="label label-warning">', gettext('Closed'), '</span> ',
                gettext('The current grade is the final grade. You can not add more deliveries unless an {examiner_term} opens the group.'),
            '</tpl>',
        '</p>',
        '<tpl if="groupinfo.is_open">',
            '<p>',
                '<a class="add_delivery_link" href="{groupinfo.add_delivery_url}">', gettext('Add delivery') ,'</a>',
            '</p>',
        '</tpl>'
    ],


    initComponent: function() {
        Ext.apply(this, {
            
        });

        this.addListener({
            element: 'el',
            delegate: 'a.active_feedback_link',
            scope: this,
            click: function(e) {
                this.fireEvent('active_feedback_link_clicked');
                e.preventDefault();
            }
        });

        this.callParent(arguments);
    }
});
