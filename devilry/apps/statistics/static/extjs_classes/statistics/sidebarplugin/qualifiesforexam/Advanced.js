Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.Advanced', {
    extend: 'devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase',
    layout: 'fit',
    requires: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.LabelConfig',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.FilterEditor',
        'devilry.statistics.sidebarplugin.qualifiesforexam.advanced.LabelConfigEditor'
    ],

    initComponent: function() {
        //Ext.apply(this, {
            //items: [{
                //xtype: 'box',
                //cls: 'readable-section',
                //html: '<strong>Coming soon.</strong> If the other methods do not cover your needs, you can track our progress towards an advanced filter on <a href="https://github.com/devilry/devilry-django/issues/236">our issue tracker</a>.'
            //}]
        //});
        Ext.apply(this, {
            items: [this.defaultButtonPanel]
        });
        this.callParent(arguments);
    },

    filter: function(student) {
        var labelConfig = Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.LabelConfig');
        labelConfig.addFilter({
            pointspec: Ext.create('devilry.statistics.sidebarplugin.qualifiesforexam.advanced.PointSpec', {
                assignments: [[this.loader.findAssignmentByShortName('extra').get('id')]],
                min: 5,
                max: undefined
            }),
            must_pass: [[this.loader.findAssignmentByShortName('week1').get('id')]]
        });
        return labelConfig.match(this.loader, student);
        //Ext.each(loader.store.data.items, function(studentRecord, index) {
            //console.log(labelConfig.match(loader, studentRecord));
        //}, this);
    }
});
