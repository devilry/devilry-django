Ext.define('devilry.statistics.dataview.LayoutBase', {
    extend: 'Ext.container.Container',
    layout: 'fit',
    config: {
        loader: undefined
    },
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.callParent(arguments);
        this.refresh();
    },

    _extjsFormatSingleAssignment: function(studentStoreFmt, assignment_id, group, storeFields, gridColumns) {
        var pointdataIndex = assignment_id + '::points';
        var scaledPointdataIndex = assignment_id + '::scaledPoints';
        var passingdataIndex = assignment_id + '::is_passing_grade';
        studentStoreFmt[pointdataIndex] = group.points;
        studentStoreFmt[scaledPointdataIndex] = group.scaled_points;
        studentStoreFmt[passingdataIndex] = group.is_passing_grade;

        if(!Ext.Array.contains(storeFields, pointdataIndex)) {
            storeFields.push(pointdataIndex);
            storeFields.push(scaledPointdataIndex);
            storeFields.push(passingdataIndex);
            gridColumns.push({
                text: group.assignment_shortname,
                //text: Ext.String.format('{0} (id: {1})', group.assignment_shortname, assignment_id),
                columns: [{
                    dataIndex: scaledPointdataIndex,
                    text: 'Scaled points',
                    sortable: true
                }, {
                    dataIndex: passingdataIndex,
                    text: 'Is passing grade',
                    sortable: true
                }]
            });
        }
    },

    _create: function() {
        var storeStudents = [];
        var storeFields = ['username', 'labels'];
        var labelTpl = Ext.create('Ext.XTemplate',
            '<ul class="labels-list">',
            '    <tpl for="labels">',
            '       <li class="label-{.}">{.}</li>',
            '    </tpl>',
            '</ul>'
        );
        var gridColumns = [{
            header: 'Username', dataIndex: 'username'
        }, {
            header: 'Labels', dataIndex: 'labels',
            width: 150,
            renderer: function(value, p, record) {
                return labelTpl.apply(record.data);
            }
        }];
        Ext.Object.each(this.loader._students, function(username, student, index) {
            var studentStoreFmt = {username: username};
            storeStudents.push(studentStoreFmt);
            studentStoreFmt['labels'] = Ext.Object.getKeys(student.labels);
            Ext.Object.each(student.groupsByAssignmentId, function(assignment_id, group, index) {
                this._extjsFormatSingleAssignment(studentStoreFmt, assignment_id, group, storeFields, gridColumns);
            }, this);

        }, this);
        return {
            storeStudents: storeStudents,
            storeFields: storeFields,
            gridColumns: gridColumns
        };
    },

    refresh: function() {
        var extjsStructures = this._create();
        var store = Ext.create('Ext.data.Store', {
            fields: extjsStructures.storeFields,
            data: {'items': extjsStructures.storeStudents},
            proxy: {
                type: 'memory',
                reader: {
                    type: 'json',
                    root: 'items'
                }
            }
        });
        this.removeAll();
        this.add({
            xtype: 'grid',
            title: 'Details',
            autoScroll: true,
            store: store,
            columns: extjsStructures.gridColumns
        });
    }
});
