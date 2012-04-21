Ext.define('devilry.statistics.activeperiods.Overview', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.activeperiods-overview',
    frame: false,
    border: false,
    autoScroll: true,
    //cls: 'selectable-grid',

    requires: [
        'devilry.extjshelpers.DateTime',
        'devilry.statistics.activeperiods.AggregatedPeriodModel',
        'devilry.extjshelpers.RestProxy',
        'devilry.extjshelpers.SearchField',
        'devilry.extjshelpers.GridSelectionModel'
    ],
    
    /**
     * @cfg
     */
    nodeRecord: undefined,


    linkTpl: Ext.create('Ext.XTemplate',
        '<a href="{DevilrySettings.DEVILRY_URLPATH_PREFIX}/administrator/period/{data.period_id}?open_students=yes&students_hidesidebar=yes">',
        '{data.subject_long_name} ({data.period_long_name})',
        '</a>'
    ),

    readyForExportTpl: Ext.create('Ext.XTemplate',
        '<tpl if="qualifies_for_exam_ready_for_export"><span class="goodInlineItem">yes</span></tpl>',
        '<tpl if="!qualifies_for_exam_ready_for_export"><span class="warningInlineItem">no</span></tpl>'
    ),

    emailLinkTpl: Ext.create('Ext.XTemplate',
        'mailto:{from}?',
        'bcc={emailAddresses}'
    ),

    emailTooltip: 'Opens your email application to send email to all admins on selected rows. Use the checkbox in the upper left corner to select all visible rows.' +
        (Ext.isIE8? '<p>WARNING: Your browser, Internet Explorer, can not handle email links containing many addresses. Use another browser if you encounter this problem.</p>': ''),
    
    initComponent: function() {
        this._createStore();
        this.selModel = Ext.create('Ext.selection.CheckboxModel', {
            checkOnly: true
        });

        Ext.apply(this, {
            tbar: [
                //xtype: 'searchfield',
                //searchdelay: 30,
                //emptyText: 'Search...',
                //width: 200,
                //listeners: {
                    //scope: this,
                    //newSearchValue: this._onNewSearchValue,
                    //emptyInput: this._onEmptySearchValue
                //}
            {
                xtype: 'button',
                iconCls: 'icon-email-16',
                text: 'Send email to admin(s) on selected',
                listeners: {
                    scope: this,
                    click: this._sendEmailsToSelected,
                    render: function(button) {
                        Ext.tip.QuickTipManager.register({
                            target: button.getEl(),
                            title: 'Click to send email to admins on selected',
                            text: this.emailTooltip,
                            width: 350,
                            dismissDelay: 30000 // Hide after 30 seconds hover
                        });
                    }
                }
            }, '->', {
                xtype: 'combobox',
                width: 350,
                valueField: 'filterfunc',
                displayField: 'label',
                forceSelection: true,
                editable: false,
                emptyText: 'Show all',
                store: Ext.create('Ext.data.Store', {
                    fields: ['filterfunc', 'label'],
                    data: [{
                        filterfunc: this._clearFilters,
                        label: 'Show all'
                    }, {
                        filterfunc: this._filterQualifiesForExamYes,
                        label: 'Show qualifies-for-exam ready for export'
                    }, {
                        filterfunc: this._filterQualifiesForExamNo,
                        label: 'Show qualifies-for-exam NOT ready for export'
                    }],
                    proxy: 'memory'
                }),
                listeners: {
                    scope: this,
                    select: function(combo, records) {
                        var record = records[0];
                        var filterfunc = record.get('filterfunc');
                        Ext.bind(filterfunc, this)();
                    }
                }
            }],
            columns: [{
                text: 'Subject',
                dataIndex: 'subject_long_name',
                flex: 30,
                renderer: function(v, m, record) {
                    return this.linkTpl.apply({
                        data: record.data,
                        DevilrySettings: DevilrySettings
                    });
                }
            },{
                text: '&laquo;Qualifies for exam&raquo; ready for export?',
                dataIndex: 'qualifies_for_exam_ready_for_export',
                width: 230,
                renderer: function(value, m, record) {
                    return this.readyForExportTpl.apply(record.data);
                }
            }],
            listeners: {
                scope: this,
                //itemmouseup: function(view, record) {
                    //var url = Ext.String.format('{0}/administrator/period/{1}?open_students=yes&students_hidesidebar=yes', DevilrySettings.DEVILRY_URLPATH_PREFIX, record.get('period_id'));
                    //window.open(url, '_blank');
                //},
                render: function() {
                    Ext.defer(function() {
                        this._createAndLoadPeriodStore();
                    }, 100, this);
                }
            }
        });
        this.callParent(arguments);
    },


    _filterQualifiesForExamYes: function() {
        this.store.clearFilter();
        this.store.filter('qualifies_for_exam_ready_for_export', true);
    },
    _filterQualifiesForExamNo: function() {
        this.store.clearFilter();
        this.store.filter('qualifies_for_exam_ready_for_export', false);
    },
    _clearFilters: function() {
        this.store.clearFilter();
    },

    //_onNewSearchValue: function(value) {
        //console.log(value);
    //},

    //_onEmptySearchValue: function() {
    //},


    _createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.statistics.activeperiods.AggregatedPeriodModel',
            autoSync: false,
            proxy: 'memory'
        });
    },

    _createAndLoadPeriodStore: function() {
        this.getEl().mask('Loading overview');
        this.periodstore = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriod',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.periodstore.proxy.setDevilryFilters([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: this.nodeRecord.get('id')
        }, {
            field: 'start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }]);
        this.periodstore.proxy.setDevilryOrderby(['-publishing_time']);
        this.periodstore.pageSize = 100000;
        this.periodstore.load({
            scope: this,
            callback: this._onPeriodStoreLoad
        });
    },

    _onPeriodStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load active periods.');
        } else {
            this._createAndLoadPeriodAppKeyValueStore();
        }
    },

    _createAndLoadPeriodAppKeyValueStore: function() {
        this.periodappkeyvalue_store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedPeriodApplicationKeyValue',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.periodappkeyvalue_store.proxy.setDevilryFilters([{
            field: 'period__parentnode__parentnode',
            comp: 'exact',
            value: this.nodeRecord.get('id')
        }, {
            field: 'period__start_time',
            comp: '<',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'period__end_time',
            comp: '>',
            value: devilry.extjshelpers.DateTime.restfulNow()
        }, {
            field: 'application',
            comp: 'exact',
            value: 'statistics-qualifiesforexam'
        }, {
            field: 'key',
            comp: 'exact',
            value: 'ready-for-export'
        }]);
        this.periodappkeyvalue_store.pageSize = 100000;
        this.periodappkeyvalue_store.load({
            scope: this,
            callback: this._onPeriodAppKeyValueStoreLoad
        });
    },

    _onPeriodAppKeyValueStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load ready-for-export status on active periods.');
        } else {
            this._createAndLoadSubjectStore();
        }
    },


    _createAndLoadSubjectStore: function() {
        this.subjectstore = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.administrator.simplified.SimplifiedSubject',
            remoteFilter: true,
            remoteSort: true,
            autoSync: true
        });

        this.subjectstore.proxy.setDevilryFilters([{
            field: 'parentnode',
            comp: 'exact',
            value: this.nodeRecord.get('id')
        }]);
        this.subjectstore.pageSize = 100000;
        this.subjectstore.load({
            scope: this,
            callback: this._onSubjectStoreLoad
        });
    },

    _onSubjectStoreLoad: function(records, op) {
        if(!op.success) {
            this._handleLoadError(op, 'Failed to load subjects.');
        } else {
            this._populateStore();
        }
    },

    _handleLoadError: function(op, title) {
        this.getEl().unmask();
        devilry.extjshelpers.RestProxy.showErrorMessagePopup(op, title);
    },

    _populateStore: function() {
        Ext.each(this.periodstore.data.items, function(periodRecord, index) {
            this.store.add({
                'period_id': periodRecord.get('id'),
                'subject_long_name': periodRecord.get('parentnode__long_name'),
                'period_long_name': periodRecord.get('long_name'),
                'qualifies_for_exam_ready_for_export': false
            });
        }, this);

        Ext.each(this.periodappkeyvalue_store.data.items, function(appKeyValueRecord, index) {
            var period_id = appKeyValueRecord.get('period');
            var periodRecord = this.periodstore.getById(period_id);
            var storeRecord = this.store.getById(period_id);
            storeRecord.set('qualifies_for_exam_ready_for_export', true);
            storeRecord.commit(); // Removed red corner
        }, this);
        this.getEl().unmask();

        this.store.sort('subject_long_name', 'ASC');
    },

    //_sendEmailsToVisible: function() {
        //var emailAddresses = this._getAdminEmailAddressesFromRecords(this.store.data.items).join(',');
        //window.location = this.emailLinkTpl.apply({
            //emailAddresses: emailAddresses
        //});
    //},

    _sendEmailsToSelected: function() {
        var selected = this.getSelectionModel().getSelection();
        if(selected.length === 0) {
            Ext.MessageBox.alert('Error', 'Please select at least one row.');
            return;
        }
        var emailAddresses = this._getAdminEmailAddressesFromRecords(selected).join(',');
        window.location = this.emailLinkTpl.apply({
            emailAddresses: emailAddresses
        });
    },

    _getAdminEmailAddressesFromRecords: function(records) {
        var emails = [];
        Ext.each(records, function(record, index) {
            var periodRecord = this.periodstore.getById(record.get('period_id'));
            var subjectid = periodRecord.get('parentnode');
            var subjectRecord = this.subjectstore.getById(subjectid);
            emails = Ext.Array.merge(emails, periodRecord.get('admins__email'));
            emails = Ext.Array.merge(emails, subjectRecord.get('admins__email'));
        }, this);
        return emails;
    }
});
