Ext.define('devilry.statistics.dataview.MinimalGridView', {
    extend: 'devilry.statistics.dataview.BaseView',

    labelTpl: Ext.create('Ext.XTemplate',
        '<ul class="labels-list">',
        '    <tpl for="labels">',
        '       <li class="label-{.}">{.}</li>',
        '    </tpl>',
        '</ul>'
    ),

    _create: function() {
        var storeStudents = [];
        this.storeFields = ['username', 'labels'];
        var me = this;
        this.gridColumns = [{
            header: 'Username', dataIndex: 'username'
        }, {
            header: 'Labels', dataIndex: 'labels',
            width: 150,
            renderer: function(value, p, record) {
                return me.labelTpl.apply(record.data);
            }
        }];
        Ext.Object.each(this.loader._students, function(username, student, index) {
            var studentStoreFmt = {username: username};
            storeStudents.push(studentStoreFmt);
            studentStoreFmt['labels'] = Ext.Object.getKeys(student.labels);
            this._extraOnEachStudent(student, studentStoreFmt);
        }, this);
        return storeStudents;
    },

    _extraOnEachStudent: function(student, studentStoreFmt) {
    },

    refresh: function() {
        var storeStudents = this._create();
        var store = Ext.create('Ext.data.Store', {
            fields: this.storeFields,
            data: {'items': storeStudents},
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
            autoScroll: true,
            store: store,
            columns: this.gridColumns
        });
    }
});
