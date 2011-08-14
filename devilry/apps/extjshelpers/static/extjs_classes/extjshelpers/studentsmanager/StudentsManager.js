Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    cls: 'studentsmanager',
    layout: 'border',
    frame: false,
    border: false,

    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid',
        'devilry.extjshelpers.studentsmanager.ManuallyCreateUsers',
        'devilry.extjshelpers.SearchField'
    ],

    config: {
        assignmentgroupstore: undefined,
        assignmentid: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            items: [{
                region: 'north',     // position for region
                xtype: 'panel',
                frame: false,
                border: false,
                height: 100,
                layout: { //Layout spec of underlying components
                    type: 'vbox',
                    align: 'center'
                },
                items: [{
                    xtype: 'searchfield',
                    width: 600,
                    height: 40,
                    padding: '30 0 0 0'

                }]
            },{
                region:'west',
                xtype: 'panel',
                width: 200,
                layout: 'fit',
                tbar: [{
                    xtype: 'button',
                    text: 'Add more students',
                    iconCls: 'icon-add-32',
                    scale: 'large',
                    width: 194,
                    listeners: {
                        scope: this,
                        click: this.onManuallyCreateUsers
                    }
                }],
                items: [{
                    xtype: 'studentsmanager_filterselector'
                }]
            },{
                region: 'center',     // center region is required, no width/height specified
                xtype: 'panel',
                layout: 'fit',
                frame: false,
                border: false,
                items: [{
                    xtype: 'studentsmanager_studentsgrid',
                    store: this.assignmentgroupstore,
                    assignmentid: this.assignmentid
                }],

                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'bottom',
                    ui: 'footer',
                    items: ['->', {
                        xtype: 'button',
                        scale: 'large',
                        text: 'Give feedback to selected',
                        listeners: {
                            scope: this,
                            click: this.onGiveFeedbackToSelected
                        }
                    }]
                }]
            }],

        });
        this.callParent(arguments);
        this.setSearchfieldAttributes();

        //this.addListener('render', function() {
            //this.up('window').addListener('show', this.onManuallyCreateUsers, this);
        //}, this);
    },

    /**
     * @private
     */
    onGiveFeedbackToSelected: function(button) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        this.getEl();
        this.down('studentsmanager_studentsgrid').performActionOnSelected({
            scope: this,
            callback: this.giveFeedbackToSelected
        });
    },

    /**
     * @private
     */
    giveFeedbackToSelected: function(record, index, total) {
        if(index == total) {
            this.getEl().unmask();
        } else {
            var msg = Ext.String.format('Processing group {0}/{1}', index, total);
            this.getEl().mask(msg);
        }
    },
    
    /**
     * @private
     */
    onManuallyCreateUsers: function() {
        var win = Ext.widget('window', {
            title: 'Create assignment groups',
            modal: true,
            width: 830,
            height: 600,
            maximizable: true,
            layout: 'fit',
            items: {
                xtype: 'manuallycreateusers',
                assignmentid: this.assignmentid
            },
            listeners: {
                scope: this,
                close: function() {
                    this.refreshStore();
                }
            }
        });
        win.show();
    },
    
    /**
     * @private
     */
    setSearchfieldAttributes: function() {
        var searchfield = this.down('searchfield');
        searchfield.addListener('newSearchValue', this.search, this);
        searchfield.addListener('emptyInput', function() {
            this.search("");
        }, this);
    },
    
    /**
     * @private
     */
    search: function(searchstring) {
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: searchstring
        });
        var extraParams = this.assignmentgroupstore.proxy.extraParams;
        this.assignmentgroupstore.proxy.extraParams = parsedSearch.applyToExtraParams(extraParams, []);
        this.assignmentgroupstore.proxy.extraParams.filters = Ext.JSON.encode([{
            field: 'parentnode',
            comp: 'exact',
            value: this.assignmentid
        }]);
        this.assignmentgroupstore.loadPage(1, {
            scope: this,
            callback: function(records, operation, success) {
                //console.log(records);
            }
        });
    },

    /**
     * @private
     * Reftesh store by re-searching for the current value.
     */
    refreshStore: function() {
        var searchfield = this.down('searchfield');
        this.search(searchfield.getValue());
    }
});
