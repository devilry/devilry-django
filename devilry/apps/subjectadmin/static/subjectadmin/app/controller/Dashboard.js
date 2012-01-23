Ext.define('subjectadmin.controller.Dashboard', {
    extend: 'Ext.app.Controller',

    views: [
        'action.List'
    ],

    refs: [{
        ref: 'actionList',
        selector: 'actionlist'
    }],

    init: function() {
        this.control({
            'viewport > actionlist': {
                beforerender: this._onBeforeActionListRender
            }
        });
    },

    _onBeforeActionListRender: function() {
        //this.getActionList()
            //data: {
                //title: 'Dashboard',
                //links: [{
                    //url: '#',
                    //text: 'Hello world'
                //}]
            //}
        //console.log('The panel was rendered');
    }
});

