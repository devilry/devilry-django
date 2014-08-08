Ext.define('devilry_student.view.add_delivery.ConfirmAfterDeadline', {
    extend: 'Ext.container.Container',
    alias: 'widget.confirm_after_deadline',

    initComponent: function() {
        Ext.apply(this, {
            margin: '20 0 0 0',
            cls: 'bootstrap',
            items: {
                xtype: 'container',
                cls: 'devilry_student_confirm_delivery_after_deadline alert alert-error',
                items: [{
                    xtype: 'box',
                    tpl: [
                        '<h3 class="alert-heading">',
                            gettext('After deadline'),
                        '</h3>',
                        '<p>',
                            interpolate(gettext('Do you really want to add a %(delivery_term)s after the %(deadline_term)s? You normally need to have a valid reason when adding %(deliveries_term)s after the %(deadline_term)s.'), {
                                delivery_term: gettext('delivery'),
                                deadline_term: gettext('deadline'),
                                deliveries_term: gettext('deliveries')
                            }, true),
                        '</p>'
                    ],
                    data: {}
                }, {
                    xtype: 'checkbox',
                    name: 'confirmafterdeadline',
                    submitValue: false,
                    value: false,
                    boxLabel: interpolate(gettext('I want to add a %(delivery_term)s after the %(deadline_term)s has expired.'), {
                        delivery_term: gettext('delivery'),
                        deadline_term: gettext('deadline')
                    }, true)
                }]
            }
        });
        this.callParent(arguments);
    }
});
