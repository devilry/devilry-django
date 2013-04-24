Ext.define('devilry_qualifiesforexam.view.summaryview.SummaryViewGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.summaryviewgrid',
    cls: 'devilry_qualifiesforexam_summaryviewgrid bootstrap',
    mixins: ['devilry_extjsextras.AutoHeightComponentMixin'],
    requires: [
        'Ext.XTemplate',
        'devilry_qualifiesforexam.utils.UrlLookup'
    ],

    disableSelection: true,
    store: 'Statuses',
    aboutColTpl: [
        '<div class="about" style="white-space:normal !important;">',
            '<div class="subjectname"><strong>{data.subject.long_name}</strong></div>',
            '<div class="periodname muted"><small>{data.long_name}</small></div>',
        '</div>'
    ],
    statusColTpl: [
        '<div class="active_status {[this.getStatusClass(values.active_status)]}" style="white-space:normal !important;">',
            '<tpl if="active_status">',
                '<tpl if="active_status.status == \'ready\'">',
                    '<strong>{active_status.statustext}</strong>',
                '<tpl else>',
                    '{active_status.statustext}',
                '</tpl>',
            '<tpl else>',
                gettext('None'),
            '</tpl>',
        '</div>', {
            getStatusClass: function(active_status) {
                if(Ext.isEmpty(active_status)) {
                    return 'muted';
                } else {
                    var classmap = {
                        ready: 'text-success',
                        almostready: 'text-info',
                        notready: 'text-warning'
                    };
                    return classmap[active_status.status];
                }
            }
        }
    ],
    actionsColTpl: [
        '<div class="actions" style="white-space:normal !important;">',
            '<tpl if="is_ready">',
                '<a href="{[this.getViewUrl(values.period_id)]}" target="_blank" class="btn btn-large">',
                    '<i class="icon-share"></i> ',
                    gettext('View'),
                '</a>',
                ' ',
                '<a href="{[this.getViewUrl(values.period_id)]}" target="_blank" class="btn btn-large btn-inverse">',
                    '<i class="icon-print icon-white"></i> ',
                    gettext('Print'),
                '</a>',
            '</tpl>',
        '</div>', {
            getViewUrl: function(period_id) {
                return devilry_qualifiesforexam.utils.UrlLookup.showstatus(period_id);
            }
        }
    ],

    constructor: function () {
        this.callParent(arguments);
        this.setupAutoHeightSizing();
        this.aboutColTplCompiled = Ext.create('Ext.XTemplate', this.aboutColTpl);
        this.statusColTplCompiled = Ext.create('Ext.XTemplate', this.statusColTpl);
        this.actionsColTplCompiled = Ext.create('Ext.XTemplate', this.actionsColTpl);
    },

    initComponent: function() {
        Ext.apply(this, {
            columns: [{
                text: gettext('Subject'),
                dataIndex: 'id',
                flex: 3,
                menuDisabled: true,
                sortable: false,
                renderer: Ext.bind(this._renderAboutCol, this)
            }, {
                text: 'Status',
                flex: 1,
                dataIndex: 'id',
                menuDisabled: true,
                sortable: false,
                minWidth: 160,
                renderer: Ext.bind(this._renderStatusCol, this)
            }, {
                text: 'Actions',
                flex: 1,
                minWidth: 80,
                renderer: Ext.bind(this._renderActionsCol, this)
            }]
        });
        this.callParent(arguments);
    },

    _renderAboutCol: function(value, meta, record) {
        return this.aboutColTplCompiled.apply({
            data: record.data
        });
    },

    _renderStatusCol: function(value, meta, record) {
        return this.statusColTplCompiled.apply({
            'active_status': record.get('active_status')
        });
    },

    _renderActionsCol: function(value, meta, record) {
        return this.actionsColTplCompiled.apply({
            'period_id': record.get('id'),
            'is_ready': !Ext.isEmpty(record.get('active_status')) && record.get('active_status').status == 'ready'
        });
    }
});
