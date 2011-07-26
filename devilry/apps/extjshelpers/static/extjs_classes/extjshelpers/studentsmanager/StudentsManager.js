Ext.define('devilry.extjshelpers.studentsmanager.StudentsManager', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.studentsmanager',
    cls: 'studentsmanager',
    layout: 'border',

    requires: [
        'devilry.extjshelpers.studentsmanager.FilterSelector',
        'devilry.extjshelpers.studentsmanager.StudentsGrid',
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
                height: 100,
                //html: 'Search will go here'
                layout: { //Layout spec of underlying components
                    type: 'vbox',
                    align: 'center'
                },
                items: [{
                    xtype: 'searchfield',
                    id: 'foo',
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
                    scale: 'large'
                }],
                items: [{
                    xtype: 'studentsmanager_filterselector'
                }]
            },{
                region: 'center',     // center region is required, no width/height specified
                xtype: 'panel',
                layout: 'fit',
                items: [{
                    xtype: 'studentsmanager_studentsgrid',
                    store: this.assignmentgroupstore,
                    assignmentid: this.assignmentid
                }],

                bbar: ['->', {
                    xtype: 'button',
                    scale: 'medium',
                    text: 'Give feedback to selected'
                }, {
                    xtype: 'button',
                    scale: 'medium',
                    text: 'Statistics'
                }]
            }],

        });
        this.callParent(arguments);
        this.setSearchfieldAttributes();
    },
    
    
    
    setSearchfieldAttributes: function() {
        var search_field = this.down('searchfield');
        var me = this;
        
        /*Add listener for searchfield input*/
        search_field.addListener('newSearchValue', this.doSomethingWithSearchFieldString, this);

        search_field.addListener('emptyInput', function() {
            console.log("StudentManager: Nil");
        });        
    
    },
    
    doSomethingWithSearchFieldString: function(value) {            
        console.log("StudentManager: " + value);
        
        var parsedSearch = Ext.create('devilry.extjshelpers.SearchStringParser', {
            searchstring: value
        });
        
        console.log(this);
        var extraParams = assignmentgroupstore.proxy.extraParams;
        assignmentgroupstore.proxy.extraParams = parsedSearch.applyToExtraParams(extraParams, []);
        console.log(assignmentgroupstore.proxy.extraParams);
        assignmentgroupstore.load({
            scope   : this,
            callback: function(records, operation, success) {
                //the operation object contains all of the details of the load operation
                console.log(records);
            }
        });
        
    }
    
});
