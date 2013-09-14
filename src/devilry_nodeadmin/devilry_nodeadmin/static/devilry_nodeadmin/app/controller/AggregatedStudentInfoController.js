Ext.define('devilry_nodeadmin.controller.AggregatedStudentInfoController', {
    extend: 'Ext.app.Controller',

    views: [
        'aggregatedstudentview.AggregatedStudentInfoOverview'
    ],

    stores: [
      'AggregatedStudentInfoStore'
    ],

    init: function() {
        this.control({
            'viewport aggregatedstudentinfo': {
                render: this._onRender
            }
        });
    },

    _onRender: function() {
      console.log('Render');
      
      this.getAggregatedStudentInfoStoreStore().load({
        scope: this,
        callback: function(records, operation) {
          console.log(records);
          this._onLoadSuccess();
        }
      });
      
    },

    _onLoadSuccess: function(records) {
      console.log('Suksess');
    }
});
