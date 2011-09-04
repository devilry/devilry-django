Ext.define('devilry.extjshelpers.studentsmanager.MultiResultWindow', {
    extend: 'Ext.window.Window',
    layout: 'fit',
    closeAction: 'hide',
    closable: false,
    width: 800,
    height: 600,
    modal: true,
    maximizable: true,

    logTpl: Ext.create('Ext.XTemplate',
        '<tpl for="log">',
        '    <section class="{parent.csscls}-small">',
        '        <h1>',
        '            <tpl if="record.data.name">',
        '               {record.data.name} -',
        '            </tpl>',
        '            <tpl for="record.data.candidates__identifier">',
        '               {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '            </tpl>',
        '        </h1>',
        '        {msg}',
        '    </section>',
        '</tpl>'
    ),

    operationErrorTpl: Ext.create('Ext.XTemplate',
        '{msg}. ',
        'Error details: {status} {statusText}.'
    ),

    constructor: function(config) {
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
                //layout: {
                    //type: 'vbox',
                    //align: 'stretch'
                //}
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

    addToLog: function(level, record, msg) {
        var logitem = {
            record: record,
            msg: msg
        }
        this.log[level].push(logitem);
        //console.log(logitem);
    },

    addError: function(record, msg) {
        this.addToLog('error', record, msg);
    },

    addErrorFromOperation: function(record, msg, operation) {
        var fullMsg = this.operationErrorTpl.apply({
            msg: msg,
            status: operation.error.status,
            statusText: operation.error.statusText
        });
        this.addToLog('error', record, fullMsg);
    },

    addWarning: function(record, msg) {
        this.addToLog('warning', record, msg);
    },

    addSuccess: function(record, msg) {
        this.addToLog('success', record, msg);
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

    createMsgHtmlList: function(log) {
        Ext.each(log, function(logitem, index) {
            
        }, this);
    },

    addIfItems: function(log, csscls, title) {
        if(log.length > 0) {
            var container = Ext.widget('panel', {
                title: title,
                bodyPadding: 10,
                flex: 1,
                autoScroll: true,
                html: this.logTpl.apply({
                    csscls: csscls,
                    log: log
                })
            });
            this.down('panel').add(container);
        }
    },

    finish: function(resultMsg, successMsg) {
        this.addIfItems(this.log.error, 'error', 'Errors');
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
        this.addIfItems(this.log.warning, 'warning', 'Warnings');
        this.addIfItems(this.log.success, 'ok', 'Details about each successful save');
        this.show();
        this.down('panel').getComponent(0).expand();
    }
});
