/**
 * A panel that displays information when no group is selected.
 */
Ext.define('devilry_subjectadmin.view.managestudents.NoGroupSelectedView' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.nogroupselectedview',
    cls: 'nogroupselectedview',

    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            padding: 20,
            autoScroll: true,
            defaults: {
                anchor: '100%'
            },
            items: [{
                xtype: 'box',
                cls: 'bootstrap',
                padding: '60 20 0 20',
                tpl: [
                    '<div>',
                        '<div class="pull-left">',
                            '<i class="icon-arrow-left"></i>',
                        '</div>',
                        '<p style="margin-left:20px;">',
                            '<strong style="font-size:160%;">',
                                gettext('Select GROUPS from the list to your left'),
                            '</strong>',
                            '<br/>',
                            '<span class="muted">',
                                gettext('Students are always in a (project) group even when they work alone.'),
                            '</span>',
                        '</p>',
                    '</div>',
                    '<div style="margin-top: 60px;">',
                        '<div class="pull-right">',
                            '<i class="icon-arrow-right"></i>',
                        '</div>',
                        '<p style="text-align:right; margin-right:20px;">',
                            '<strong style="font-size:160%;">',
                                gettext('Click the help-column to your right if you need help'),
                            '</strong>',
                            '<br/>',
                            '<span class="muted">',
                                gettext('First time visitors should read the help to avoid common misconceptions.'),
                            '</span>',
                        '</p>',
                    '</div>'
                ],
                data: {}
            }]
        });
        this.callParent(arguments);
    }
});
