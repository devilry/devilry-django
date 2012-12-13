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
                            '<span class="{[this.getRelativeTimeCls(values.is_published)]}">',
                                '{[this.formatRelativeDatetime(values.publishing_time_offset_from_now, values.is_published)]} ',
                            '</span>',
                            '({[this.formatDatetime(values.publishing_time)]})',
                        '</small>',
                    '<div>',
                '</p></li>',
            '</tpl>',
        '<ul>', {
            formatDatetime: function(datetime) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeLong(datetime);
            },
            formatRelativeDatetime: function(publishing_time_offset_from_now, is_published) {
                return devilry_extjsextras.DatetimeHelpers.formatTimedeltaRelative(
                    publishing_time_offset_from_now, !is_published);
            },
            getRelativeTimeCls: function(is_published) {
                return is_published? 'text-success': 'text-warning';
            }
        }
    ],
    itemSelector: 'li.devilry_assignment'
});
