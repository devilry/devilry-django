Ext.define('devilry.statistics.OverviewOfSingleStudent', {
    extend: 'Ext.Component',
    alias: 'widget.statistics-overviewofsinglestudent',
    requires: [
        'devilry.statistics.OverviewOfSingleStudentRecord'
    ],
    
    /**
     * @cfg {Object} [groupInfos]
     */

    /**
     * @cfg {Object} [assignment_store]
     */

    /**
     * @cfg {Object} [labels]
     */

    tpl: [
        '<div style="margin-bottom: 5px">',
        '   <ul class="labels-list">',
        '       <tpl for="labels">',
        '          <li class="label-{label}">{label}</li>',
        '       </tpl>',
        '   </ul>',
        '</div>',
        '<table class="horizontalinfotable">',
        '   <thead><tr>',
        '       <th>Assignment</th>',
        '       <th>Points (no scaling)</th>',
        '       <th>Grade</th>',
        '       <th>Passing grade?</th>',
        '       <th>Open?</th>',
        '   </tr></thead>',
        '   <tbody>',
        '      <tpl for="items">',
        '         <tr>',
        '             <td><a href="{parent.DEVILRY_URLPATH_PREFIX}/administrator/assignmentgroup/{data.id}" target="_blank">{data.assignment__long_name}</a></td>',
        '             <td><tpl if="data.feedback !== null">',
        '                {data.feedback.points}',
        '             </tpl></td>',
        '             <td><tpl if="data.feedback !== null">',
        '                {data.feedback.grade}',
        '             </tpl></td>',
        '             <td>',
        '                 <tpl if="data.feedback === null">',
        '                    <span class="nofeedback">No feedback</span>',
        '                 <tpl else>',
        '                    <tpl if="data.feedback.is_passing_grade">Yes</tpl>',
        '                    <tpl if="!data.feedback.is_passing_grade">No</tpl>',
        '                 </tpl>',
        '             </td>',
        '             <td>',
        '                <tpl if="data.is_open">Yes</tpl>',
        '                <tpl if="!data.is_open">No</tpl>',
        '             </td>',
        '         </tr>',
        '      </tpl>',
        '   </tbody>',
        '   <tfoot>',
        '      <tr>',
        '          <td>Total points</td>',
        '          <td>{total_points}</td>',
        '      </tr>',
        '   </tfoot>',
        '</table>'
    ],

    padding: 10,
    
    initComponent: function() {
        this.total_points = 0;
        var storeData = [];
        Ext.each(this.groupInfos, function(groupInfo, index) {
            var assignmentRecord = this.assignment_store.getById(groupInfo.assignment_id);
            this.total_points += groupInfo.feedback === null? 0: groupInfo.feedback.points;
            var data = {
                id: groupInfo.id,
                is_open: groupInfo.is_open,
                feedback: groupInfo.feedback,
                assignmentid: assignmentRecord.get('id'),
                assignment__short_name: assignmentRecord.get('short_name'),
                assignment__long_name: assignmentRecord.get('long_name')
            };
            storeData.push(data);
        }, this);
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.OverviewOfSingleStudentRecord',
            autoSync: false,
            proxy: 'memory',
            data: storeData
        });

        this.DEVILRY_URLPATH_PREFIX = DevilrySettings.DEVILRY_URLPATH_PREFIX;
        Ext.apply(this, {
            data: {
                items: this.store.data.items,
                labels: this.labels,
                total_points: this.total_points
            }
        });
        this.callParent(arguments);
    }
});
