/** A grid containing search results.
 *
 * @xtype searchresults
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResults', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.searchresults',
    config: {
        /**
         * @cfg
         * Editor url prefix (__Required__). The editor url for a specific
         * item is ``editorurlprefix+id``. Note that this means that editorurlprefix _must_
         * end with ``/``.
         */
        editorurlprefix: ''
    },

    //statics: {
        //onButtonClick: function(button, urlprefix) {
            ////var query = Ext.String.format('div.searchresults-row:has(#{0})', button.id);
            ////var domnode = Ext.DomQuery.selectNode(query);
            ////var row = Ext.getCmp(domnode.id);
            ////console.log(button.parentNode.parentNode);
            //console.log(urlprefix);
        //}
    //},

    initComponent: function() {
        Ext.apply(this, {
            width: 570,
            margin: {
                top: 20
            },
            //height: 150,
            frame: false,
            //title: false,
            hideHeaders: true,
            columns: [{
                header: 'Items', dataIndex: 'id', flex: 1,
                renderer: this.formatRowWrapper
            }],
            dockedItems: [{
                xtype: 'pagingtoolbar',
                store: this.store,   // same store GridPanel is using
                dock: 'top',
                displayInfo: true
            }]
        });
        this.callParent(arguments);
    },

    formatRowWrapper: function(value, p, record) {
        return this.formatRow(record);
    },

    formatRow: function(record) {
        var datatpl = Ext.create('Ext.XTemplate', this.rowformattpl);
        var dataview = datatpl.apply(record.data);
        var tpl = Ext.create('Ext.XTemplate', 
            '<div class="searchresults-row">' +
            '   <input type="hidden" name="{idprefix}-recordid" value="{record.data.id}" />' +
            '   <div class="links"><tpl for="links">' +
            '       <a class="{cssclass}" ' +
            //'           onclick="devilry.extjshelpers.searchwidget.SearchResults.onButtonClick(this, \'{urlprefix}\'); return false;"' +
            '           href="{urlprefix}{parent.record.data.id}">{title}</a>' +
            '   </tpl></div>' +
            '   <div>{dataview}</div>' +
            '</div>');

        return tpl.apply({
            dataview: dataview,
            links: this.links,
            idprefix: this.id,
            record: record
        });
    },

    listeners: {
        //selectionchange: function(view, selections, options) {
            //var record = selections[0].data;
            //window.location = Ext.String.format('{0}{1}',  this.editorurlprefix, record.id);
        //}
    },

    deselectAll: function() {
        Ext.each(this.ownerCt.items.items, function(grid, index, resultgrids) {
            grid.getSelectionModel().deselectAll();
        });
    }
});
