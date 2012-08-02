Ext.define('devilry.extjshelpers.studentsmanager.MultiResultWindow', {
    extend: 'Ext.window.Window',
    layout: 'fit',
    closeAction: 'hide',
    closable: false,
    width: 600,
    height: 400,
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
        '                <tpl for="assgnmentGroupRecord.data.candidates">',
        '                   {identifier}<tpl if="xindex &lt; xcount">, </tpl>',
        '                </tpl>',
        '            </tpl>',
        '        </h1>',
        '        {msg}',
        '    </div>',
        '</tpl>'
    ),

    operationErrorTpl: Ext.create('Ext.XTemplate',
        '{msg}. ',
        '<tpl if="status === 0">',
        '    Error details: Could not connect to the Devilry server.',
        '</tpl>',
        '<tpl if="status !== 0">',
        '    (Error code: {status}) Error details: <strong>{statusText}</strong>',
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

    _createErrorMessageFromResponseData: function(responseData) {
        if(typeof responseData.items === 'undefined') {
            throw "responseData.items == undefined";
        }
        var messages = [];

        var fieldErrors = responseData.items.fielderrors;
        if(typeof fieldErrors !== 'undefined') {
            Ext.Object.each(fieldErrors, function(fieldname, errormessages) {
                if(fieldname !== '__all__') { // Note: We assume __all__ is also in errormessages, which is added below
                    messages.push(Ext.String.format('{0}: {1}', fieldname, errormessages.join('. ')));
                }
            }, this);
        }

        var globalErrors = responseData.items.errormessages;
        if(typeof globalErrors !== 'undefined') {
            Ext.Array.each(globalErrors, function(errormessage) {
                messages.push(errormessage);
            }, this);
        }

        return messages;
    },

    addErrorFromOperation: function(assgnmentGroupRecord, msg, operation) {
        var errormessage = operation.error.statusText;
        try {
            var responseData = Ext.JSON.decode(operation.response.responseText);
            var messages = this._createErrorMessageFromResponseData(responseData);
            if(messages.length > 0) {
                errormessage = messages.join('<br/>');
            }
        } catch(e) {
            // Ignore decode errors (we just use the generic statusText instead.
        }
        var fullMsg = this.operationErrorTpl.apply({
            msg: msg,
            status: operation.error.status,
            statusText: errormessage
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
