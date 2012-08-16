Ext.define('devilry_student.view.dashboard.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.dashboard',
    cls: 'devilry_student_dashboard',

    frame: false,
    border: 0,
    bodyPadding: 20,
    autoScroll: true,
    layout: 'column',

    items: [{
        xtype: 'container',
        columnWidth: 0.65,
        items: [{
            xtype: 'container',
            itemId: 'notExpired',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: [
                    '<h2>{heading} <small>- {heading_suffix}</small></h2>'
                ],
                data: {
                    heading: gettext('Assignments'),
                    heading_suffix: interpolate(gettext('click one to add a %(delivery_term)s'), {
                        delivery_term: gettext('delivery')
                    }, true)
                }
            }, {
                xtype: 'opengroups_deadline_not_expired_grid'
            }]
        }, {
            xtype: 'container',
            itemId: 'expired',
            margin: '30 0 0 0',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: [
                    '<h3>{heading}</h3>',
                    '<p><small>{subheading}</small></p>'
                ],
                data: {
                    heading: interpolate(gettext('%(assignments_term)s with expired %(deadlines_term)s'), {
                        assignments_term: gettext('Assignments'),
                        deadlines_term: gettext('deadlines')
                    }, true),
                    subheading: interpolate(gettext('These %(assignments_term)s use soft deadlines, so you are allowed to add %(deliveries_term)s even if the deadline has expired. You normally need a valid reason to add %(deliveries_term)s after a %(deadline_term)s has expired, and your %(examiner_term)s will clearly see any deliveries made after the deadline.'), {
                        assignments_term: gettext('assignments'),
                        deadlines_term: gettext('deadlines'),
                        deadline_term: gettext('deadline'),
                        deliveries_term: gettext('deliveries'),
                        examiner_term: gettext('examiner')
                    }, true),
                }
            }, {
                xtype: 'opengroups_deadline_expired_grid'
            }]
        }, {
            xtype: 'container',
            itemId: 'old'
        }]
    }, {
        xtype: 'container',
        padding: '0 0 0 40',
        columnWidth: 0.35,
        items: {
            xtype: 'container',
            itemId: 'recentDeliveries',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: [
                    '<h4>{heading}</h4>'
                ],
                data: {
                    heading: interpolate(gettext('Recent %(deliveries_term)s'), {
                        deliveries_term: gettext('deliveries')
                    }, true)
                }
            }, {
                xtype: 'recentdeliveriesgrid'
            }]
        }
    }]
});
