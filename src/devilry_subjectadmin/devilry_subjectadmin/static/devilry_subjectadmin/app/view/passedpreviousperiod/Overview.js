Ext.define('devilry_subjectadmin.view.passedpreviousperiod.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.passedpreviousperiodoverview',
    cls: 'devilry_subjectadmin_passedpreviousperiodoverview',
    requires: [
        'devilry_subjectadmin.view.passedpreviousperiod.SelectGroupsGrid'
    ],

    /**
     * @cfg {String} assignment_id (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            bodyPadding: '20 40 20 40',
            layout: 'border',
            border: false,

            items: [{
                xtype: 'box',
                region: 'north',
                height: 70,
                cls: 'bootstrap',
                html: [
                    '<h1>',
                        interpolate(gettext('Passed in previous %(period_term)s'), {
                            period_term: gettext('period')
                        }, true),
                    '</h1>'
                    ].join('')
            }, {
                xtype: 'container',
                region: 'center',
                layout: 'card',
                itemId: 'cardContainer',
                items: [{
                    xtype: 'container',
                    itemId: 'pageOne',
                    layout: 'border',
                    items: [{
                        xtype: 'selectpassedpreviousgroupsgrid',
                        region: 'center',

                        fbar: ['->', {
                            xtype: 'button',
                            scale: 'large',
                            text: gettext('Next'),
                            disabled: true,
                            itemId: 'nextButton'
                        }]
                    }, {
                        xtype: 'box',
                        region: 'east',
                        width: 300,
                        cls: 'bootstrap',
                        padding: '0 0 0 30',
                        html: [
                            '<p class="muted">',
                                gettext('Select one or more groups. Groups that we belive have passed this assignment before has been selected automatically, and they are marked with the name of the old assignment.'),
                            '</p>',
                            '<p class="muted"><small>',
                                gettext('The search for previously passed students match the short name of old assignments against the short name of this assignment. Only groups with exactly one student in both the old and the current assignment is matched.'),
                            '</small></p>'
                        ].join('')
                    }]
                }, {
                    xtype: 'container',
                    itemId: 'pageTwo',
                    items: [{
                        xtype: 'box',
                        html: 'Hello world'
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    }
});
