Ext.define('devilry_nodeadmin.controller.AggregatedStudentInfoController', {
    extend: 'Ext.app.Controller',

    views: [
        'aggregatedstudentview.AggregatedStudentInfoOverview'
    ],

    stores: [],

    init: function() {
        this.control({
            'viewport aggregatedstudentinfo': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
        console.log('Render');
    }

    //_onLoadSuccess: function(records) {
        //this.getAllWhereIsAdminList().update({
            //loadingtext: null,
            //list: this._flattenListOfActive(records)
        //});
    //}
});
