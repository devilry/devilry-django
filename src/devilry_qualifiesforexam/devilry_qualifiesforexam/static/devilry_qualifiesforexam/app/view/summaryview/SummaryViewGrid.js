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
            '<tpl if="can_view">',
                '<a href="{[this.getViewUrl(values.period_id)]}" target="_blank" class="btn btn-large">',
                    '<i class="icon-share"></i> ',
                    gettext('View'),
                '</a>',
            '</tpl>',
            '<tpl if="is_ready">',
                ' ',
                '<a href="{[this.getPrintUrl(values.status_id)]}" target="_blank" class="btn btn-large btn-inverse">',
                    '<i class="icon-print icon-white"></i> ',
                    gettext('Print'),
                '</a>',
            '</tpl>',
        '</div>', {
            getViewUrl: function(period_id) {
                return devilry_qualifiesforexam.utils.UrlLookup.showstatus(period_id);
            },
            getPrintUrl: function(status_id) {
                return devilry_qualifiesforexam.utils.UrlLookup.showstatus_print(status_id);
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
                text: gettext('Status'),
                flex: 1,
                dataIndex: 'id',
                menuDisabled: true,
                sortable: false,
                minWidth: 160,
                renderer: Ext.bind(this._renderStatusCol, this)
            }, {
                text: gettext('Actions'),
                flex: 1,
                minWidth: 200,
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
        var active_status = record.get('active_status');
        return this.actionsColTplCompiled.apply({
            'period_id': record.get('id'),
            'status_id': Ext.isEmpty(active_status)? undefined: active_status.id,
            'is_ready': !Ext.isEmpty(active_status) && active_status.status == 'ready',
            'can_view': !Ext.isEmpty(active_status)
        });
    }
});
