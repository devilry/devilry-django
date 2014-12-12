Ext.define('devilry.extjshelpers.studentsmanager.MultiResultWindow', {

    /**
     * @cfg {bool} [isAdministrator]
     */
    isAdministrator: undefined,

    logTpl: [
        '<p>{title}. {MORE_BUTTON}</p>',
        '<dl {MORE_ATTRS}>',
            '<tpl for="log">',
                '<dt>',
                    '<tpl if="assgnmentGroupRecord.data.name">',
                        '{assgnmentGroupRecord.data.name} -',
                    '</tpl>',
                    '<tpl if="parent.isAdministrator">',
                        '<tpl for="assgnmentGroupRecord.data.candidates__student__username">',
                            '{.}<tpl if="xindex &lt; xcount">, </tpl>',
                        '</tpl>',
                    '</tpl>',
                    '<tpl if="!parent.isAdministrator">',
                        '<tpl for="assgnmentGroupRecord.data.candidates">',
                            '{identifier}<tpl if="xindex &lt; xcount">, </tpl>',
                        '</tpl>',
                    '</tpl>',
                '</dt>',
                '<dd>{msg}</dd>',
            '</tpl>',
        '</dl>'
    ],

    operationErrorTplArray: [
        '{msg}. ',
        '<tpl if="status === 0">',
        '    Error details: Could not connect to the Devilry server.',
        '</tpl>',
        '<tpl if="status !== 0">',
        '    (Error code: {status}) Error details: <strong>{statusText}</strong>',
        '</tpl>'
    ],

    constructor: function(config) {
        this.operationErrorTpl = Ext.create('Ext.XTemplate', this.operationErrorTplArray);
    },

    addToLog: function(level, assgnmentGroupRecord, msg) {
        var logitem = {
            assgnmentGroupRecord: assgnmentGroupRecord,
            msg: msg
        };
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
        this.title = title;
    },

    /**
     * @private
     */
    _addIfItems: function(log, type, title, autoclose) {
        if(log.length > 0) {
            window.getFloatingAlertMessageList().add({
                type: type,
                messagetpl: this.logTpl,
                autoclose: autoclose,
                messagedata: {
                    log: log,
                    title: title,
                    isAdministrator: this.isAdministrator
                }
            });
        }
    },

    finish: function(successMsg) {
        this._addIfItems(this.log.error, 'error', interpolate(gettext('%(count)s error(s) during: %(title)s'), {
            title: this.title,
            count: this.log.error.length
        }, true));
        this._addIfItems(this.log.warning, 'warning', interpolate(gettext('%(count)s warning(s) during: %(title)s'), {
            title: this.title,
            count: this.log.warning.length
        }, true));

        var total = this.log.error.length + this.log.warning.length + this.log.success.length;
        if(Ext.isEmpty(successMsg)) {
            successMsg = interpolate(gettext('%(title)s &mdash; %(count)s/%(total)s groups successfully updated'), {
                count: this.log.success.length,
                total: total,
                title: this.title
            }, true);
        }
        this._addIfItems(this.log.success, 'success', successMsg, 14);
    }
});
