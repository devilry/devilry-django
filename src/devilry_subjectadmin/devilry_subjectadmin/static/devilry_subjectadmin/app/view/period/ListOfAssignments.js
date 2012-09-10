/**
 * List of assignments within a period.
 */
Ext.define('devilry_subjectadmin.view.period.ListOfAssignments', {
    extend: 'Ext.view.View',
    alias: 'widget.listofassignments',
    cls: 'devilry_listofassignments bootstrap',
    store: 'Assignments',

    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    tpl: [
        '<ul class="unstyled">',
            '<tpl for=".">',
                '<li class="devilry_assignment"><p>',
                    '<div class="name">',
                        '<a href="#/assignment/{id}/">{long_name}</a> ',
                    '</div>',
                    '<div class="assignmentmeta">',
                        '<small class="muted">',
                            '<em>',
                                gettext('Publishing time'),
                            ': </em>',
                            '{[this.formatRelativeDatetime(values.publishing_time_offset_from_now, values.is_published)]} ',
                            '({[this.formatDatetime(values.publishing_time)]})',
                        '</small>',
                    '<div>',
                '</p></li>',
            '</tpl>',
        '<ul>', {
            formatDatetime: function(datetime) {
                return Ext.Date.format(datetime, 'Y-m-d h:i');
            },
            formatRelativeDatetime: function(publishing_time_offset_from_now, is_published) {
                return devilry_extjsextras.DatetimeHelpers.formatTimedeltaRelative(
                    publishing_time_offset_from_now, !is_published);
            }
        }
    ],
    itemSelector: 'li.devilry_assignment'
});
