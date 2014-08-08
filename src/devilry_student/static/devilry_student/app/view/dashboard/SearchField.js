Ext.define('devilry_student.view.dashboard.SearchField', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.dashboard_searchfield',
    cls: 'devilry_student_dashboard_searchfield',

    queryMode: 'remote',
    store: 'FindGroups',
    displayField: 'id',
    typeAhead: false,
    hideLabel: true,
    hideTrigger: true,
    queryDelay: 250,
    minChars: 2,

    emptyText: interpolate(gettext('Search your %(assignments_term)s ...'), {
        assignments_term: gettext('assignments')
    }, true),

    listConfig: {
        loadingText: gettext('Searching') + ' ...',
        emptyText: gettext('Nothing matches your search'),
        getInnerTpl: function () {
            return [
                '<div class="bootstrap">',
                    '{subject.short_name} - {assignment.long_name}',
                '</div>',
                '<div><small>',
                    '{subject.short_name}.{period.short_name}.{assignment.short_name}',
                '</small></span>'
            ].join('');
        }
    }
});
