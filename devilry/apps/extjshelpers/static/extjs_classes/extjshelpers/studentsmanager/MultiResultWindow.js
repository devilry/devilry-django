Ext.define('devilry.extjshelpers.studentsmanager.MultiResultWindow', {
    extend: 'Ext.window.Window',
    layout: 'fit',
    closeAction: 'hide',
    closable: false,
    width: 800,
    height: 600,
    modal: true,
    maximizable: true,

    config: {
        isAdministrator: undefined
    },

    logTpl: Ext.create('Ext.XTemplate',
        '<tpl for="log">',
        '    <div class="section {parent.csscls}-small">',
        '        <h1>',
        '            <tpl if="assgnmentGroupRecord.data.name">',
        '               {assgnmentGroupRecord.data.name} -',
        '            </tpl>',
        '            <tpl if="parent.isAdministrator">',
        '                <tpl for="assgnmentGroupRecord.data.candidates__student__username">',
        '                   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '                </tpl>',
        '            </tpl>',
        '            <tpl if="!parent.isAdministrator">',
        '                <tpl for="assgnmentGroupRecord.data.candidates__identifier">',
        '                   {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '                </tpl>',
        '            </tpl>',
        '        </h1>',
        '        {msg}',
        '    </div>',
        '</tpl>'
    ),

    operationErrorTpl: Ext.create('Ext.XTemplate',
        '{msg}. ',
        'Error details: ',
        '<tpl if="status === 0">',
        '    Could not connect to the Devilry server.',
        '</tpl>',
        '<tpl if="status !== 0">',
        '    {status} {statusText}.',
        '</tpl>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.errorcontainer = Ext.widget('panel', {
            title: 'Errors',
            bodyPadding: 10
        });
        this.warningcontainer = Ext.widget('panel', {
            title: 'Warnings',
            bodyPadding: 10
        });
        this.successcontainer = Ext.widget('panel', {
            title: 'Successful',
            bodyPadding: 10
        });
        Ext.apply(this, {
            items: {
                xtype: 'panel',
                border: false,
                layout: 'accordion'
            },
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    text: 'Close this window',
                    scale: 'large',
                    listeners: {
                        scope: this,
                        click: function() {
                            this.close();
                        }
                    }
                }, '->']
            }]
        });
        this.callParent(arguments);
    },

    addToLog: function(level, assgnmentGroupRecord, msg) {
        
        var logitem = {
            assgnmentGroupRecord: assgnmentGroupRecord,
            msg: msg
        }
        this.log[level].push(logitem);
    },

    addError: function(assgnmentGroupRecord, msg) {
        this.addToLog('error', assgnmentGroupRecord, msg);
    },

    addErrorFromOperation: function(assgnmentGroupRecord, msg, operation) {
        var fullMsg = this.operationErrorTpl.apply({
            msg: msg,
            status: operation.error.status,
            statusText: operation.error.statusText
        });
        this.addToLog('error', assgnmentGroupRecord, fullMsg);
    },

    addWarning: function(assgnmentGroupRecord, msg) {
        this.addToLog('warning', assgnmentGroupRecord, msg);
    },

    addSuccess: function(assgnmentGroupRecord, msg) {
        this.addToLog('success', assgnmentGroupRecord, msg);
    },


    start: function(title) {
        this.log = {
            error: [],
            warning: [],
            success: []
        };
        this.setTitle(title);
        this.down('panel').removeAll();
    },

    /**
     * @private
     */
    _addIfItems: function(log, csscls, title) {
        if(log.length > 0) {
            var container = Ext.widget('panel', {
                title: title,
                bodyPadding: 10,
                flex: 1,
                autoScroll: true,
                html: this.logTpl.apply({
                    csscls: csscls,
                    log: log,
                    isAdministrator: this.isAdministrator
                })
            });
            this.down('panel').add(container);
        }
    },

    finish: function(resultMsg, successMsg) {
        this._addIfItems(this.log.error, 'error', 'Errors');
        if(successMsg && this.log.error.length === 0) {
            this.down('panel').add({
                xtype: 'panel',
                title: successMsg.title,
                html: successMsg.html,
                bodyPadding: 10,
                flex: 1
            });
        }
        if(resultMsg) {
            this.down('panel').add({
                xtype: 'panel',
                title: resultMsg.title,
                html: resultMsg.html,
                bodyPadding: 10,
                flex: 1
            });
        }
        this._addIfItems(this.log.warning, 'warning', 'Warnings');
        this._addIfItems(this.log.success, 'info', 'Details about each successful save');
        this.show();
        this.down('panel').getComponent(0).expand();
    }
});
