Ext.define('devilry.markup.MarkdownFullEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.markdownfulleditor',
    layout: 'fit',

    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                cls: 'edit-toolbar',
                dock: 'top',
                items: [{
                    xtype: 'button',
                    text: 'h1',
                    cls: 'headbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onH1
                    }
                }, {
                    xtype: 'button',
                    text: 'h2',
                    cls: 'headbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onH2
                    }
                }, {
                    xtype: 'button',
                    text: 'h3',
                    cls: 'headbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onH3
                    }
                }, {xtype: 'box', width: 15}, {
                    xtype: 'button',
                    text: 'b',
                    cls: 'bbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onBold
                    }
                }, {
                    xtype: 'button',
                    text: 'i',
                    cls: 'ibtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onItalic
                    }
                }, {
                    xtype: 'button',
                    text: '{}',
                    scale: 'medium',
                    cls: 'codebtn',
                    listeners: {
                        scope: this,
                        click: this.onCode
                    }
                }, {
                    xtype: 'button',
                    text: 'a',
                    cls: 'linkbtn',
                    scale: 'medium',
                    listeners: {
                        scope: this,
                        click: this.onUrl
                    }
                }, '->', {
                    xtype: 'button',
                    text: '?',
                    cls: 'helpbtn',
                    scale: 'medium',
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
