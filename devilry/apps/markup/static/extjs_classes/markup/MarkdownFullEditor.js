Ext.define('devilry.markup.MarkdownFullEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.markdownfulleditor',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'top',
                items: [{
                    xtype: 'button',
                    text: 'h1',
                    listeners: {
                        scope: this,
                        click: this.onH1
                    }
                }, {
                    xtype: 'button',
                    text: 'h2',
                    listeners: {
                        scope: this,
                        click: this.onH2
                    }
                }, {
                    xtype: 'button',
                    text: 'h3',
                    listeners: {
                        scope: this,
                        click: this.onH3
                    }
                }, {xtype: 'box', width: 10}, {
                    xtype: 'button',
                    text: 'b',
                    listeners: {
                        scope: this,
                        click: this.onBold
                    }
                }, {
                    xtype: 'button',
                    text: 'i',
                    listeners: {
                        scope: this,
                        click: this.onItalic
                    }
                }, {
                    xtype: 'button',
                    text: '{}',
                    listeners: {
                        scope: this,
                        click: this.onCode
                    }
                }, {
                    xtype: 'button',
                    text: 'a',
                    listeners: {
                        scope: this,
                        click: this.onUrl
                    }
                }, {xtype: 'box', width: 10}, {
                    xtype: 'button',
                    text: '-',
                    listeners: {
                        scope: this,
                        click: this.onBulletList
                    }
                }, {
                    xtype: 'button',
                    text: '1.',
                    listeners: {
                        scope: this,
                        click: this.onNumberedList
                    }
                }, {
                    xtype: 'button',
                    text: '" "',
                    listeners: {
                        scope: this,
                        click: this.onBlockQuote
                    }
                }, '->', {
                    xtype: 'button',
                    text: '',
                    iconCls: 'icon-help-32',
                    scale: 'large',
                    listeners: {
                        scope: this,
                        click: this.onHelp
                    }
                }]
            }],
            items: [{
                xtype: 'textareafield'
            }]
        });
        this.callParent(arguments);
    },

    onH1: function() {
        this.surroundCursorSelection('\n# ', '');
    },
    onH2: function() {
        this.surroundCursorSelection('\n## ', '');
    },
    onH3: function() {
        this.surroundCursorSelection('\n### ', '');
    },

    onBold: function() {
        this.surroundCursorSelection('**');
    },
    onItalic: function() {
        this.surroundCursorSelection('_');
    },
    onCode: function() {
        this.surroundCursorSelection('`');
    },
    onUrl: function() {
        this.surroundCursorSelection('[', '](http://)');
    },

    onBulletList: function() {
        this.surroundCursorSelection('\n- ', '');
    },
    onNumberedList: function() {
        this.surroundCursorSelection('\n1. ', '');
    },
    onBlockQuote: function() {
        this.surroundCursorSelection('\n> ', '');
    },


    onHelp: function() {
        console.log('Help meee');
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
        if(suffix == undefined) {
            suffix = prefix;
        }
        var selection = this.getCursorSelection();
        var curText = this.getValue();
        var textPrefix = curText.substring(0, selection.start);
        var textSuffix = curText.substring(selection.end, curText.length);
        var selectionText = curText.substring(selection.start, selection.end);
        var result = textPrefix + prefix + selectionText + suffix + textSuffix;
        this.setValue(result);

        var cursorPosition = selection.start + prefix.length;
        this.getField().selectText(cursorPosition, cursorPosition);
    }
});
