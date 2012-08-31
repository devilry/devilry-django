Ext.define('devilry_subjectadmin.view.gradeeditor.Edit' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.gradeeditoredit',
    cls: 'devilry_subjectadmin_gradeeditoredit',

    layout: 'anchor',
    defaults: {
        anchor: '100%'
    },
    items: [{
        xtype: 'box',
        itemId: 'about',
        cls: 'bootstrap',
        tpl: [
            '<tpl if="registryitem">',
                '<h2>',
                    gettext('Current grade editor'),
                    ': {registryitem.title}',
                    ' <a href="#" class="change_gradeeditor_link">(',
                        gettext('Change'),
                    ')</a>',
                '</h2>',
                '<div>',
                    '{registryitem.description}',
                '</div>',
            '<tpl else>',
                '<h3>', gettext('Loading') + ' ...', '</h3>',
            '</tpl>'
        ],
        data: {
        }
    }, {
        xtype: 'container',
        itemId: 'configContainer',
        layout: 'fit',
        items: []
    }]
});
