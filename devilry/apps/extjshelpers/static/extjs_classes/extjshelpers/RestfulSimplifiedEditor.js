/** 
 * @xtype extjshelpers
 * */
Ext.define('devilry.extjshelpers.RestfulSimplifiedEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.administratoreditorscudform',

    initComponent: function() {
        Ext.apply(this.form, {
            title: 'Center Region',
            region: 'center',     // center region is required, no width/height specified
            margins: '0 0 0 0'
        });

        Ext.apply(this, {
            layout: 'border',
            //frame: false,
            //title: false,
            //hideHeaders: true,
            items: [{
                title: 'Actions',
                region: 'east',     // position for region
                collapsible: true,   // make collapsible
                titleCollapse: true,
                collapsed: false,
                xtype: 'panel',
                width: 150,
                split: true,         // enable resizing
                margins: '0 0 0 0',
                html: "Some buttons here (such as create)"
            }, this.form],
        });
        this.callParent(arguments);
    }
});
