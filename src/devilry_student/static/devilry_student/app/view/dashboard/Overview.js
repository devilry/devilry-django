Ext.define('devilry_student.view.dashboard.Overview' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.dashboard',
    cls: 'devilry_student_dashboard',

    padding: 20,
    autoScroll: true,
    layout: 'column',

    items: [{
        xtype: 'container',
        columnWidth: 0.65,
        items: [{
            xtype: 'container',
            itemId: 'notExpired',
            cls: 'devilry_focuscontainer',
            padding: 20,
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: '<h1 style="margin-top: 0;">{heading} <small>- {heading_suffix}</small></h1>',
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
            itemId: 'notExpiredEmpty',
            hidden: true,
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: [
                    '<h1>{heading}</h1>',
                    '<p><small>{subheading}</small></p>'
                ],
                data: {
                    heading: gettext('Assignments'),
                    subheading: interpolate(gettext('You have no active electronic %(assignments_term)s.'), {
                        assignments_term: gettext('assignments')
                    }, true)
                }
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
                    '<p><small class="muted">{subheading}</small></p>'
                ],
                data: {
                    heading: interpolate(gettext('%(assignments_term)s with expired %(deadlines_term)s'), {
                        assignments_term: gettext('Assignments'),
                        deadlines_term: gettext('deadlines')
                    }, true),
                    subheading: interpolate(gettext('These %(assignments_term)s use soft %(deadlines_term)s, so you are allowed to add %(deliveries_term)s even though the %(deadline_term)s has expired. You normally need a valid reason to add %(deliveries_term)s after a %(deadline_term)s has expired, even on %(assignments_term)s with soft deadlines.'), {
                        assignments_term: gettext('assignments'),
                        deadlines_term: gettext('deadlines'),
                        deadline_term: gettext('deadline'),
                        deliveries_term: gettext('deliveries')
                    }, true)
                }
            }, {
                xtype: 'opengroups_deadline_expired_grid'
            }]
        }, {
            xtype: 'box',
            cls: 'bootstrap',
            margin: '30 0 0 0',
            tpl: [
                '<h3>',
                    gettext('Navigate'),
                '</h3>',
                '<ul class="unstyled">',
                    '<li>',
                        '<strong><a href="#/browsegrouped/active">',
                            gettext('Active {period_term}'),
                        '</a></strong>',
                        '<small class="muted"> - ',
                            gettext('Quick overview of your assignments'),
                        '</small>',
                    '</li>',
                    //'<li>',
                        //'<strong><a href="#/browse/">',
                            //gettext('Calendar of active {period_term}'),
                        //'</a></strong>',
                    //'</li>',
                    //'<li>',
                        //'<strong><a href="#/browsegrouped/">',
                            //gettext('Qualified for final exams?'),
                        //'</a></strong>',
                        //'<small class="muted"> - ',
                            //gettext('Status for all {subjects_term} in active {periods_term}'),
                        //'</small>',
                    //'</li>',
                    '<li>',
                        '<strong><a href="#/browsegrouped/history">',
                            gettext('History'),
                        '</a></strong>',
                        '<small class="muted"> - ',
                            gettext('Browse all your assignments'),
                        '</small>',
                    '</li>',
                '</ul>'
            ],
            data: {
                subjects_term: gettext('subjects'),
                periods_term: gettext('periods'),
                period_term: gettext('period')
            }
        }]
    }, {
        xtype: 'container',
        border: 0,
        padding: '0 0 0 40',
        columnWidth: 0.35,
        layout: 'anchor',
        items: [{
            xtype: 'toolbar',
            dock: 'top',
            ui: 'footer',
            margin: 0,
            padding: 0,
            items: [{
                xtype: 'dashboard_searchfield',
                flex: 1
            }]
        }, {
            xtype: 'container',
            itemId: 'recentDeliveries',
            margin: '20 0 0 0',
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
        }, {
            xtype: 'container',
            margin: '20 0 0 0',
            itemId: 'recentFeedbacks',
            anchor: '100%',
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                tpl: [
                    '<h4>{heading}</h4>'
                ],
                data: {
                    heading: interpolate(gettext('Recent %(feedbacks_term)s'), {
                        feedbacks_term: gettext('feedbacks')
                    }, true)
                }
            }, {
                xtype: 'recentfeedbacksgrid'
            }]
        }]
    }]
});
