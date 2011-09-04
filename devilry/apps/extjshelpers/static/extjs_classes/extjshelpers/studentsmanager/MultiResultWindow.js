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
        '            <tpl for="record.data.candidates__identifier">',
        '               {.}<tpl if="xindex &lt; xcount">, </tpl>',
        '            </tpl>',
        '        </h1>',
        '        {msg}',
        '    </section>',
        '</tpl>'
    ),

    constructor: function(config) {
        this.log = {
            error: [],
            warning: [],
            success: []
        };
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
                    text: 'Close',
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

    addWarning: function(record, msg) {
        this.addToLog('warning', record, msg);
    },

    addSuccess: function(record, msg) {
        this.addToLog('success', record, msg);
    },


    start: function(title) {
        this.setTitle(title);
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

    finish: function() {
        this.addIfItems(this.log.error, 'error', 'Errors');
        this.addIfItems(this.log.warning, 'warning', 'Warnings');
        this.addIfItems(this.log.success, 'ok', 'Success');
        this.show();
    }
});
