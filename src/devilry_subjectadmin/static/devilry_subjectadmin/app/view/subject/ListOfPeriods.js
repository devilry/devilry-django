/**
 * List of periods within a subject.
 */
Ext.define('devilry_subjectadmin.view.subject.ListOfPeriods', {
    extend: 'Ext.view.View',
    alias: 'widget.listofperiods',
    cls: 'devilry_listofperiods bootstrap',
    store: 'Periods',

    tpl: [
        '<ul class="unstyled">',
            '<tpl for=".">',
                '<li class="devilry_period">',
                    '<div class="name"><a href="#/period/{id}/">{long_name}</a></div> ',
                    '<div class="startendtime">',
                        '<small class="muted">',
                            '{[this.formatDatetime(values.start_time)]}',
                            ' &mdash; ',
                            '{[this.formatDatetime(values.end_time)]}',
                        '</small>',
                    '<div>',
                '</li>',
            '</tpl>',
        '<ul>', {
            formatDatetime: function(datetime) {
                return devilry_extjsextras.DatetimeHelpers.formatDateTimeShort(datetime);
            }
        }
    ],
    itemSelector: 'li.period'
});
