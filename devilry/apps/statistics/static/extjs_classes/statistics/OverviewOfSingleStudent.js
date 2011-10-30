Ext.define('devilry.statistics.OverviewOfSingleStudent', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-overviewofsinglestudent',
    
    config: {
        role: undefined,
        periodid: undefined,
        userid: undefined
    },
    
    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);

        this.candidate_store = Ext.create('Ext.data.Store', {
            model: Ext.String.format('devilry.apps.{0}.simplified.SimplifiedCandidate', this.role),
            remoteFilter: true,
            remoteSort: true
        });
    },
    
    initComponent: function() {
        Ext.apply(this, {
        });
        this.callParent(arguments);
    },

    _loadAssignmentGroups: function() {
        this.candidate_store.pageSize = 100000; // TODO: avoid UGLY hack
        this.candidate_store.proxy.setDevilryFilters([{
            field: 'assignment_group__parentnode__parentnode',
            comp: 'exact',
            value: this.periodid
        }, {
            field: 'student',
            comp: 'exact',
            value: this.userid
        }]);
        this.candidate_store.load({
            scope: this,
            callback: this._onCandidatesLoaded
        });
    },

    _onCandidatesLoaded: function(records) {
        console.log(records);
    }
});
