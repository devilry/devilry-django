Ext.define('devilry.extjshelpers.charts.PointsOfGroupsOnSingleAssignment', {
    extend: 'Ext.chart.Chart',
    alias: 'widget.chart_pointsofgroupsonsingleassignment',
    cls: 'widget-chart_pointsofgroupsonsingleassignment',

    groupTpl: Ext.create('Ext.XTemplate',
        '<tpl for="candidates">',
        '   {.}<tpl if="xindex != xcount">, </tpl>',
        '</tpl>'
    ),

    hoverTpl: Ext.create('Ext.XTemplate',
        '<tpl for="candidates__identifier">',
        '   {.}<tpl if="xindex != xcount">, </tpl>',
        '</tpl>:',
        'points: {feedback__points}'
    ),

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            style: 'background:#fff',
            animate: true,
            shadow: true,
            axes: [{
                type: 'Numeric',
                position: 'bottom',
                fields: ['feedback__points'],
                label: {
                    renderer: Ext.util.Format.numberRenderer('0,0')
                },
                title: 'Points',
                grid: true,
                minimum: 0
            }, {
                type: 'Category',
                position: 'left',
                fields: ['candidates__identifier'],
                title: 'Group',

                label: {
                    renderer: function(data) {
                        return me.groupTpl.apply({candidates: data});
                    }
                },
            }],
            series: [{
                type: 'bar',
                axis: 'bottom',
                highlight: true,
                tips: {
                    trackMouse: true,
                    width: 140,
                    height: 28,
                    renderer: function(storeItem, item) {
                        this.setTitle(me.hoverTpl.apply(storeItem.data));
                    }
                },
                label: {
                    display: 'insideEnd',
                    'text-anchor': 'middle',
                    field: 'feedback__points',
                    renderer: Ext.util.Format.numberRenderer('0'),
                    orientation: 'vertical',
                    color: '#333'
                },
                xField: 'id',
                yField: 'feedback__points',

                renderer: function(sprite, record, attr, index, store) {
                    var color = record.get('feedback__is_passing_grade')? 'green': 'red';
                    return Ext.apply(attr, {
                        fill: color
                    });
                }

            }]
        });
        this.callParent(arguments);
    }
});
