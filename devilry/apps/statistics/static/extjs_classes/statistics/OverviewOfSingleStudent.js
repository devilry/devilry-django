Ext.define('devilry.statistics.OverviewOfSingleStudent', {
    extend: 'Ext.container.Container',
    alias: 'widget.statistics-overviewofsinglestudent',
    requires: [
        'devilry.statistics.OverviewOfSingleStudentRecord',
        'devilry.statistics.SingleStudentPeriodChart'
    ],
    
    config: {
        username: undefined,
        full_name: undefined,
        labels: undefined,
        assignmentgroups: undefined,
        assignment_store: undefined,
        labelKeys: undefined
    },

    mainTpl: Ext.create('Ext.XTemplate',
        '<div style="margin-bottom: 5px">',
        '   <ul class="labels-list">',
        '       <tpl for="labelKeys">',
        '          <li class="label-{.}">{.}</li>',
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
        '      <tpl for="store.data.items">',
        '         <tr>',
        '             <td><a href="{parent.DEVILRY_URLPATH_PREFIX}/administrator/assignmentgroup/{data.id}" target="_blank">{data.assignment__long_name}</a></td>',
        '             <td>{data.feedback__points}</td>',
        '             <td>{data.feedback__grade}</td>',
        '             <td>',
        '                 <tpl if="data.feedback === null">',
        '                    <span class="nofeedback">No feedback</span>',
        '                 </tpl>',
        '                 <tpl if="data.feedback !== null">',
        '                    <tpl if="data.feedback__is_passing_grade">Yes</tpl>',
        '                    <tpl if="!data.feedback__is_passing_grade">No</tpl>',
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
    ),

    autoScroll: true,
    padding: 10,
    
    constructor: function(config) {
        this.initConfig(config);

        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.OverviewOfSingleStudentRecord',
            autoSync: false,
            proxy: 'memory'
        });
        this.total_points = 0;
        Ext.each(this.assignmentgroups, function(assignmentgroup, index) {
            var assignmentRecord = this.assignment_store.getById(assignmentgroup.parentnode);
            this.total_points += assignmentgroup.feedback__points;
            this.store.add({
                id: assignmentgroup.id,
                assignmentid: assignmentRecord.get('id'),
                assignment__short_name: assignmentRecord.get('short_name'),
                assignment__long_name: assignmentRecord.get('long_name'),
                is_open: assignmentgroup.is_open,
                feedback: assignmentgroup.feedback,
                feedback__points: assignmentgroup.feedback__points,
                feedback__grade: assignmentgroup.feedback__grade,
                feedback__is_passing_grade: assignmentgroup.feedback__is_passing_grade
            });
        }, this);

        this.callParent([config]);
    },
    
    initComponent: function() {
        this.DEVILRY_URLPATH_PREFIX = DevilrySettings.DEVILRY_URLPATH_PREFIX;
        Ext.apply(this, {
            layout: {
                type: 'hbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'box',
                html: this.mainTpl.apply(this),
                flex: 6
            }, {
                xtype: 'statistics-singlestudentperiodchart',
                store: this.store,
                flex: 4
            }]
        });
        this.callParent(arguments);
    },

    //_loadAssignmentGroups: function() {
        //this.candidate_store = Ext.create('Ext.data.Store', {
            //model: Ext.String.format('devilry.apps.{0}.simplified.SimplifiedCandidate', this.role),
            //remoteFilter: true,
            //remoteSort: true
        //});
        //this.candidate_store.pageSize = 100000; // TODO: avoid UGLY hack
        //this.candidate_store.proxy.setDevilryFilters([{
            //field: 'assignment_group__parentnode__parentnode',
            //comp: 'exact',
            //value: this.periodid
        //}, {
            //field: 'student',
            //comp: 'exact',
            //value: this.userid
        //}]);
        //this.candidate_store.load({
            //scope: this,
            //callback: this._onCandidatesLoaded
        //});
    //},

    //_onCandidatesLoaded: function(records) {
        //console.log(records);
    //}
});
