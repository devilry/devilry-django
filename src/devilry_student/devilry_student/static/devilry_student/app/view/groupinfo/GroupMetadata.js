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
            '<tpl if="groupinfo.candidates.length &gt; 1">',
                '<h3>', gettext('Students'), '</h3>',
                '<ul class="studentslist">',
                '<tpl for="groupinfo.candidates">',
                    '<li>',
                        '<a href="mailto:{user.email}">',
                            '{user.displayname}',
                        '</a>',
                    '</li>',
                '</tpl>',
                '</ul>',
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
                    '<ul>',
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

        '<div class="gradeblock">',
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
        '</div>',

        '<div class="statusblock">',
            '<h3>', gettext('Status'), '</h3>',
            '<p class="statuspara">',
                '<tpl if="groupinfo.is_open">',
                    '<span class="label label-success">', gettext('Open'), '</span> ',
                    interpolate(gettext('You can add more %(deliveries_term)s.'), {
                        deliveries_term: gettext('deliveries')
                    }, true),
                '<tpl else>',
                    '<span class="label label-warning">', gettext('Closed'), '</span> ',
                    interpolate(gettext('The current %(grade_term)s is the final grade. You can not add more %(deliveries_term)s unless an %(examiner_term)s opens the group.'), {
                        deliveries_term: gettext('deliveries'),
                        examiner_term: gettext('examiner'),
                        grade_term: gettext('grade')
                    }, true),
                '</tpl>',
            '</p>',
        '</div>',


        '<div class="deliveriesblock">',
            '<h3>', gettext('Deliveries'), '</h3>',
            '<tpl if="deliveries">',
                '<tpl if="deliveries.length &gt; 0">',
                    '<ul>',
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
            '<tpl if="groupinfo.is_open">',
                '<p>',
                    '<strong><a class="add_delivery_link" href="#/group/{groupinfo.id}/@@add-delivery">',
                        interpolate(gettext('Add %(delivery_term)s'), {
                            delivery_term: gettext('delivery')
                        }, true),
                    '</a></strong>',
                '</p>',
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
