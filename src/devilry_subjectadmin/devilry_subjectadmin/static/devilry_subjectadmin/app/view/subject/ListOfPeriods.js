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
                '<li class="devilry_period"><p>',
                    '<div class="name"><a href="#/period/{id}/">{long_name}</a></div> ',
                    '<div class="timespan">',
                        '<small class="muted">',
                            '{[this.formatDatetime(values.start_time)]}',
                            ' &mdash; ',
                            '{[this.formatDatetime(values.end_time)]}',
                        '</small>',
                    '<div>',
                '</p></li>',
            '</tpl>',
        '<ul>', {
            formatDatetime: function(datetime) {
                return Ext.Date.format(datetime, 'Y-m-d h:i');
            }
        }
    ],
    itemSelector: 'li.period'
});
