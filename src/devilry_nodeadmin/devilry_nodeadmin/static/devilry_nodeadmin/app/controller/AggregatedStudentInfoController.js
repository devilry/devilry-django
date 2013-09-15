Ext.define('devilry_nodeadmin.controller.AggregatedStudentInfoController', {
    extend: 'Ext.app.Controller',

    views: [
        'aggregatedstudentview.AggregatedStudentInfoOverview'
    ],

  refs: [
    {ref: 'AggregatedStudentInfoBox',
     selector: '#AggregatedStudentInfoBox'
    }],

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
          if (operation.success) {
            this._onLoadSuccess(records);
          } else {
            this._onLoadFailure();
          }
          
        }
      });
      
    },

    _onLoadSuccess: function(records) {
      console.log('Sucess');
      console.log(records[0].data);
      this.getAggregatedStudentInfoBox().update({data: records[0].data});
    },

  _onLoadFailure: function(records){
    console.log('failure');
  }

});
