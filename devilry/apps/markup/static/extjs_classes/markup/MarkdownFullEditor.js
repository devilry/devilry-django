Ext.define('devilry.markup.MarkdownFullEditor', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.markdownfulleditor',
    layout: 'fit',
    requires: [
        'devilry.extjshelpers.HelpWindow'
    ],

    markdownHelp: Ext.create('Ext.XTemplate',
        '   <h1>Devilry-flavoured markdown</h1>',
        '   <p>Devilry uses a special configuration of a markup language named Markdown.</p>',
        '   <ul class="right_toc">',
        '       <li><a href="#{idprefix}-block-elements">Block elements</a>',
        '           <ul>',
        '               <li><a href="#{idprefix}-para">Paragraphs</a></li>',
        '               <li><a href="#{idprefix}-headers">Headers</a></li>',
        '               <li><a href="#{idprefix}-blockquotes">Blockquotes</a></li>',
        '               <li><a href="#{idprefix}-lists">Lists</a></li>',
        '               <li><a href="#{idprefix}-codeblocks">Code/unformatted</a></li>',
        '           </ul>',
        '       </li>',
        '       <li><a href="#{idprefix}-inline-elements">Inline elements</a>',
        '           <ul>',
        '               <li><a href="#{idprefix}-links">Links</a></li>',
        '               <li><a href="#{idprefix}-emphasis">Emphasis</a></li>',
        '               <li><a href="#{idprefix}-code">Code</a></li>',
        '           </ul>',
        '       </li>',
        '       <li><a href="#{idprefix}-escaping">Escaping</a></li>',
        '       <li><a href="#{idprefix}-math">LaTeX math</a>',
        '           <ul>',
        '               <li><a href="#{idprefix}-inlinemath">Inline</a></li>',
        '               <li><a href="#{idprefix}-blockmath">Block</a></li>',
        '           </ul>',
        '       </li>',
        '   </ul>',


        '   <h2 id="{idprefix}-block-elements">Block elements</h2>',
        '   <h3 id="{idprefix}-para">Paragraphs and Breaks</h3>',
        '   <p>To create a paragraph, simply create a block of text that is not separated by one or more blank lines. Blocks of text separated by one or more blank lines will be parsed as paragraphs.</p>',
        '   <p>If you want to create a line break, end a line with two or more spaces, then hit Return/Enter.</p>',
        
        '   <h3 id="{idprefix}-headers">Headers</h3>',
        '   <p>Write the header text on its own line. Prefix your header text with the number of # characters to specify heading depth. For example:<br/><code># Heading 1</code><br/><code>## My Heading 2</code></p>',
        '   <p></p>',

        '   <h3 id="{idprefix}-blockquotes">Blockquotes</h3>',
        '   <p>Markdown creates blockquotes email-style by prefixing each line with the >. This looks best if you decide to hard-wrap text and prefix each line with a > character, but Markdown supports just putting > before your paragraph.</p>',

        '   <h3 id="{idprefix}-lists">Lists</h3>',
        '   <p>Markdown supports both ordered and unordered lists. To create an ordered list, simply prefix each line with a number (any number will do). To create an unordered list, you can prefix each line with <strong>-</strong>.</p>',

        '   <h3 id="{idprefix}-codeblocks">Code/unformatted blocks</h3>',
        '   <p>Markdown wraps code blocks in pre-formatted tags to preserve indentation in your code blocks. To create a code block, indent the entire block by at least 4 spaces. Markdown will strip the extra indentation you’ve added to the code block.</p>',
        '   <p>To get <strong>syntax highlighting</strong>, add <code>:::somelanguage</code> at the top of a code block. For example:</p>',
        '   <pre>    :::python\n    def sum(a, b):\n        return a + b</pre>',
        '   <p>The syntax hilighter uses Pygments. Check out the <a href="https://github.com/devilry/devilry-django/wiki/Markdown">Devilry wiki</a> for supported programming languages.</p>',


        '   <h2 id="{idprefix}-inline-elements">Inline elements</h2>',
        '   <h3 id="{idprefix}-links">Links</h3>',
        '   <p>To create a link, create a pair of brackets surrounding your link text, immediately followed by a pair of parentheses and write your URL within the parentheses. Example: <code>[Devilry website](http://devilry.org)</code>.</p>',
        '   <p>If you want to create a link that displays the actual URL, markdown allows you to quickly wrap the URL in &lt; and &gt; to do so. For example, the link <a href="http://devilry.org">http://devilry.org</a> is easily produced by writing <code>&lt;http://devilry.org&gt;</code>.</p>',
        
        '   <h3 id="{idprefix}-emphasis">Emphasis</h3>',
        '   <p>Surround you text by single underscore (i.e.: <code>_my text_</code>) for italic text, and by double asterisks (i.e.: <code>**my text**</code>) for bold text.</p>',

        '   <h3 id="{idprefix}-code">Code</h3>',
        '   <p>To create inline spans of code, simply wrap the code in backticks (`). Markdown will turn `myFunction` into <code>myFunction</code>.</p>',


        '   <h2 id="{idprefix}-escaping">Escaping</h2>',
        '   <p>If you want to use a special Markdown character in your document (such as displaying literal asterisks), you can escape the character with a backslash. Markdown will ignore the character directly after a backslash. Example:</p>',
        '   <pre>This is how the &#92;_ (underscore) and &#92;* asterisks characters look.</pre>',

        '   <h2 id="{idprefix}-math">LaTeX Math</h2>',
        '   <p>We provide two methods for writing <a href="http://www.mathjax.org/">MathJax</a> compatible math. <strong>Note:</strong> You must escape <em>backslash</em> as <a href="#{idprefix}-escaping">described above</a>.</p>',

        '   <h3 id="{idprefix}-inlinemath">Inline</h3>',
        '   <p>For inline math, use <code>$math$your math here$/math$</code>. For example:</p>',
        '   <pre>You know that $math$2^3 = 10$/math$ right?</pre>',

        '   <h3 id="{idprefix}-blockmath">Block</h3>',
        '   <p>For a block of math (a centered paragrath), use <code>$mathBlock$your math here$/mathBlock$</code>. For example:</p>',
        '   <pre>$mathblock$\n^3/_7\n$/mathblock$</pre>'
    ),

    initComponent: function() {
        this.helpwindow = Ext.widget('helpwindow', {
            title: 'Devilry-flavoured markdown',
            closeAction: 'hide',
            helptext: this.markdownHelp.apply(idprefix=this.getId())
        });


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

    /**
     * @private
     */
    onH1: function() {
        this.surroundCursorSelection('\n# ', '');
    },
    /**
     * @private
     */
    onH2: function() {
        this.surroundCursorSelection('\n## ', '');
    },
    /**
     * @private
     */
    onH3: function() {
        this.surroundCursorSelection('\n### ', '');
    },

    /**
     * @private
     */
    onBold: function() {
        this.surroundCursorSelection('**');
    },
    /**
     * @private
     */
    onItalic: function() {
        this.surroundCursorSelection('_');
    },
    /**
     * @private
     */
    onCode: function() {
        this.surroundCursorSelection('`');
    },
    /**
     * @private
     */
    onUrl: function() {
        this.surroundCursorSelection('[', '](http://)');
    },

    /**
     * @private
     */
    onBulletList: function() {
        this.surroundCursorSelection('\n- ', '');
    },
    /**
     * @private
     */
    onNumberedList: function() {
        this.surroundCursorSelection('\n1. ', '');
    },
    /**
     * @private
     */
    onBlockQuote: function() {
        this.surroundCursorSelection('\n> ', '');
    },


    /**
     * @private
     */
    getValue: function() {
        return this.getField().getValue();
    },

    /**
     * @private
     */
    setValue: function(value) {
        this.getField().setValue(value);
    },

    /**
     * @private
     */
    getField: function() {
        return this.down('textareafield');
    },

    /**
     * @private
     */
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
    
    /**
     * @private
     */
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
    },


    /**
     * @private
     */
    onHelp: function() {
        this.helpwindow.show();
    }
});
