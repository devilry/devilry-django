Ext.define('devilry.tutorialstats.BarChart', {
    chart: null,
    requires: 'devilry.tutorialstats.RestPeriodPointsModel',

    constructor: function(renderTo) {
        this.renderTo = renderTo;
        return this;
    },

    create_store: function(periodpoints_url) {
        return Ext.create('Ext.data.Store', {
            model: 'devilry.tutorialstats.RestPeriodPointsModel',
            autoLoad: true,
            autoSync: true,
            proxy: {
                type: 'rest',
                url: periodpoints_url,
                reader: {
                    type: 'json',
                    root: 'items'
                }
            }
        });
    },

    create_chart: function(store) {
        this.chart = Ext.create('Ext.chart.Chart', {
            width: 600,
            height: 400,
            store: store,
            renderTo: this.renderTo,

            // Define axes
            axes: [{
                type: 'Numeric',
                position: 'bottom',
                fields: ['sumperiod'],
                title: 'Points this period',
                minimum: 0
            }, {
                type: 'Category',
                position: 'left',
                fields: ['username'],
                title: 'Student'
            }],

            // Define series
            series: [{
                type: 'bar',
                axis: 'bottom',
                xField: 'username',
                yField: ['sumperiod']
            }]
        });
    },


    refresh: function(periodpoints_url) {
        var store = this.create_store(periodpoints_url);

        if(this.chart != null) {
            this.chart.bindStore(store);
        } else {
            this.create_chart(store);
        }

    }
});
