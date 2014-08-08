Ext.define('devilry_student.view.groupinfo.GroupMetadata' ,{
    extend: 'Ext.Component',
    alias: 'widget.groupmetadata',
    cls: 'bootstrap devilry_student_groupmetadata',

    tpl: [
        '<div class="groupnameblock">',
            '<tpl if="groupinfo.name">',
                '<h3>', gettext('Group name'), '</h3>',
                '<p class="groupname">{groupinfo.name}</p>',
            '</tpl>',
        '</div>',

        '<div class="candidatesblock">',
            '<tpl if="groupinfo.candidates.length &gt; 1 || groupinfo.students_can_create_groups_now">',
                '<h3>',
                    gettext('Group members'),
                '</h3>',
                '<ul class="studentslist unstyled">',
                '<tpl for="groupinfo.candidates">',
                    '<li>',
                        '<a href="mailto:{user.email}">',
                            '{user.displayname}',
                        '</a>',
                    '</li>',
                '</tpl>',
                '</ul>',
                '<tpl if="groupinfo.students_can_create_groups_now">',
                    '<strong><a href="groupinvite/overview/{groupinfo.id}">',
                        gettext('Invite students to the group'),
                    '</strong></a>',
                '</tpl>',
            '</tpl>',
        '</div>',

        '<div class="examinersblock">',
            '<tpl if="groupinfo.examiners !== null">',
                '<h3>',
                    '<tpl if="groupinfo.examiners.length &gt; 1">',
                        gettext('Examiners'),
                    '<tpl else>',
                        gettext('Examiner'),
                    '</tpl>',
                '</h3>',

                '<tpl if="groupinfo.examiners.length == 0">',
                    '<p><small>',
                        interpolate(gettext('No %(examiner)s'), {
                            examiner: gettext('examiner')
                        }, true),
                    '</small></p>',
                '<tpl elseif="groupinfo.examiners.length == 1">',
                    '<tpl for="groupinfo.examiners">',
                        '<p><a href="mailto:{user.email}">',
                            '{user.displayname}',
                        '</a></p>',
                    '</tpl>',
                '<tpl else>',
                    '<ul class="unstyled">',
                        '<tpl for="groupinfo.examiners">',
                            '<li>',
                                '<a href="mailto:{user.email}">',
                                    '{user.displayname}',
                                '</a>',
                            '</li>',
                        '</tpl>',
                    '</ul>',
                '</tpl>',
            '</tpl>',
        '</div>',

        '<tpl if="groupinfo.status === \'corrected\'">',
            '<div class="gradeblock">',
                '<h3>', gettext('Grade'), '</h3>',
                '<p>',
                    '<tpl if="groupinfo.active_feedback == null">',
                        '<small class="no_feedback_message">', gettext('No feedback'), '</small>',
                    '<tpl else>',
                        '<tpl if="groupinfo.active_feedback.feedback.is_passing_grade">',
                            '<span class="text-success">', gettext('Passed') ,'</span>',
                        '<tpl else>',
                            '<span class="text-warning">', gettext('Failed') ,'</span>',
                        '</tpl>',
                        ' <small>({groupinfo.active_feedback.feedback.grade})</small>',
                        ' - <a class="active_feedback_link" href="#/group/{groupinfo.id}/{groupinfo.active_feedback.delivery_id}">', gettext('Details'), '</a>',
                    '</tpl>',
                '</p>',
            '</div>',

        '<tpl else>',
            '<div class="statusblock">',
                '<h3>', gettext('Status'), '</h3>',
                '<p class="statuspara statuspara-{groupinfo.status}">',
                    '<tpl if="groupinfo.status === \'waiting-for-deliveries\'">',
                        '<em><small class="muted">',
                            gettext('Waiting for deliveries, or for deadline to expire'),
                        '</small></em>',
                    '<tpl elseif="groupinfo.status === \'waiting-for-feedback\'">',
                        '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                    '<tpl else>',
                        '<span class="label label-important">{groupinfo.status}</span>',
                    '</tpl>',
                '</p>',
            '</div>',
        '</tpl>',

        '<div class="deliveriesblock">',
            '<h3>', gettext('Deliveries'), '</h3>',
            '<tpl if="deliveries">',
                '<tpl if="deliveries.length &gt; 0">',
                    '<ul class="unstyled">',
                        '<tpl for="deliveries">',
                            '<li><a class="delivery_link" href="#/group/{parent.groupinfo.id}/{id}" data-deliveryid="{id}">',
                                gettext('Delivery'), ' #{number}',
                            '</a></li>',
                        '</tpl>',
                    '</ul>',
                '</tpl>',
            '</tpl>',
        '</div>',

        '<div class="adddeliveryblock">',
            '<tpl if="can_add_deliveries">',
                '<p>',
                    '<strong><a class="add_delivery_link" href="#/group/{groupinfo.id}/@@add-delivery">',
                        interpolate(gettext('Add %(delivery_term)s'), {
                            delivery_term: gettext('delivery')
                        }, true),
                    '</a></strong>',
                '</p>',
            '<tpl elseif="hard_deadline_expired">',
                '<span class="label label-important">', gettext('Deadline expired'), '</span> ',
                interpolate(gettext('Your %(deadline_term)s has expired. This %(assignment_term)s uses hard %(deadlines_term)s, so you can not add more %(deliveries_term)s.'), {
                    deadline_term: gettext('deadline'),
                    assignment_term: gettext('assignment'),
                    deadlines_term: gettext('deadlines'),
                    deliveries_term: gettext('deliveries')
                }, true),
            '</tpl>',
        '</div>'
    ],


    initComponent: function() {
        this.addListener({
            element: 'el',
            delegate: 'a.active_feedback_link',
            scope: this,
            click: function(e) {
                this.fireEvent('active_feedback_link_clicked');
                e.preventDefault();
            }
        });
        this.addListener({
            element: 'el',
            delegate: 'a.delivery_link',
            scope: this,
            click: function(e) {
                var element = Ext.dom.Element(e.target);
                this.fireEvent('delivery_link_clicked', element.getAttribute('data-deliveryid'));
                e.preventDefault();
            }
        });

        this.callParent(arguments);
    }
});
