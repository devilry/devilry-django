Ext.define('devilry.markup.MarkdownFullEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.markdownfulleditor',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            tbar: [{
                xtype: 'button',
                text: 'b',
                listeners: {
                    scope: this,
                    click: this.onBold
                }
            }],
            items: [{
                xtype: 'textareafield'
            }]
        });
        this.callParent(arguments);
    },

    onBold: function() {
        this.setValue(this.surroundCursorSelection('**'));
    },


    getValue: function() {
        return this.getField().getValue();
    },

    setValue: function(value) {
        this.getField().setValue(value);
    },

    getField: function() {
        return this.down('textareafield');
    },

    getCursorSelection: function() {
        var field = this.getField().inputEl;
        if (Ext.isIE) {
            var bookmark = document.selection.createRange().getBookmark();
            var selection = field.dom.createTextRange();
            selection.moveToBookmark(bookmark);

            var before = field.dom.createTextRange();
            before.collapse(true);
            before.setEndPoint("EndToStart", selection);

            var selLength = selection.text.length;

            var start = before.text.length;
            return {
                start: start,
                end: start + selLength
            };
        } else {
            return {
                start: field.dom.selectionStart,
                end: field.dom.selectionEnd
            };
        }
    },
    
    surroundCursorSelection: function(prefix, suffix) {
        suffix = suffix || prefix;
        var selection = this.getCursorSelection();
        var curText = this.getValue();
        var textPrefix = curText.substring(0, selection.start);
        var textSuffix = curText.substring(selection.end, curText.length);
        var selectionText = curText.substring(selection.start, selection.end);
        return textPrefix + prefix + selectionText + suffix + textSuffix;
    }
});
