Ext.define('devilry.extjshelpers.GridPrintButton', {
    //extend: 'Ext.button.Split',
    extend: 'Ext.button.Button',
    alias: 'widget.gridprintbutton',

    initComponent: function() {
        Ext.apply(this, {
            text: 'Print',
            iconCls: 'icon-print-16',
            tooltip: {
                title: 'Open print formatted table in new window.',
                text: 'Use the print button/menu item in your browser to print the table.'
            }
            //menu: [{
                //text: 'Print format',
                //listeners: {
                    //scope: this,
                    //click: this._onPrintFormat
                //}
            //}]
        });
        this.on('click', this._onPrint, this);
        this.callParent(arguments);
    },

    _onPrint: function() {
        this.fireEvent('printformat');
    }

    //_onPrintFormat: function() {
        //this.fireEvent('printformat');
    //}
});
