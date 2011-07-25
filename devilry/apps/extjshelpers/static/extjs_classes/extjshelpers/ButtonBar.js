/** A button bar containing {@link devilry.extjshelpers.ButtonBarButton} many.
 *
 * Add buttons as items to the container.
 * */
Ext.define('devilry.extjshelpers.ButtonBar', {
    extend: 'Ext.container.Container',
    requires: ['devilry.extjshelpers.ButtonBarButton'],
    border: 0,
    height: 40,
    layout: {
        type: 'hbox',
        align: 'stretch',
        pack: 'center'
    }
});
