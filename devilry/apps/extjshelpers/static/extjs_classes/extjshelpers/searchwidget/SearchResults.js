/** A panel containing multiple search results under a common title and store.
 *
 *      ------------------------
 *      | title                |
 *      ------------------------
 *      | result 1             |
 *      | result 2             |
 *      | result 3             |
 *      -----------------------|
 *
 * @xtype searchresults
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.searchresults',
    requires: ['devilry.extjshelpers.searchwidget.SearchResultItem'],
    config: {
        /**
         * @cfg
         * Editor url prefix (__Required__). The editor url for a specific
         * item is ``editorurlprefix+id``. Note that this means that editorurlprefix _must_
         * end with ``/``. _Required_.
         */
        editorurlprefix: undefined,

        /**
         * @cfg
         * Title of these search results. _Required_.
         */
        title: undefined,

        /**
         * @cfg
         * The ``Ext.data.store`` where the results are loaded from. _Required_.
         */
        store: undefined,

        /**
         * @cfg
         * Formatting template for the text rendered for each result item. _Required_.
         */
        rowformattpl: undefined
    },

    initComponent: function() {
        Ext.apply(this, {
            width: 570,
            margin: {
                top: 20
            },
            //height: 150,
            frame: false,
            //title: false,
            hideHeaders: true
        });
        this.callParent(arguments);

        var me = this;
        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.handleStoreLoadSuccess(records);
            } else {
                me.handleStoreLoadFailure();
            }
        });
    },

    handleStoreLoadFailure: function() {
        console.log('Failed to load store'); // TODO Better error handling
    },

    handleStoreLoadSuccess: function(records) {
        var me = this;
        Ext.each(records, function(record) {
            me.addRecord(record);
        });
    },

    addRecord: function(record) {
        console.log(record);
        this.add({
            xtype: 'searchresultitem',
            tpl: this.rowformattpl,
            record: record
        });
    }


    /*
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
    */
});
