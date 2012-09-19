/**
 * A component for information display. Works just like a regular component,
 * except that it adds an extra attribute, ``MORE_BUTTON``, to the template
 * data. This extra attribute, inserts a button in the markup that toggles
 * the visibility of any element in the component with the ``.more`` css class.
 *
 * Example:
 *      {
 *          xtype: 'markupmoreinfobox',
 *          tpl: [
 *              'Always visible {MORE_BUTTON}',
 *              '<p {MORE_ATTRS}>Shown when more button is clicked.</p>'
 *          ],
 *          data: {}
 *      }
 *
 * Note that we use {MORE_ATTRS}, which simply inserts ``class="more" style="display: none;"``.
 */
Ext.define('devilry_extjsextras.MarkupMoreInfoBox', {
    extend: 'Ext.Component',
    alias: 'widget.markupmoreinfobox',
    border: false,
    frame: false,

    /**
     * @cfg {String} [lesstext="Less info"]
     * The text to show on the Less info button. The default text is translated.
     */
    lesstext: gettext('Less info') + ' ...',

    /**
     * @cfg {String} [lesstext="More info ..."]
     * The text to show on the More info button. The default text is translated.
     */
    moretext: gettext('More info') + ' ...',

    initComponent: function() {
        this.morebutton = [
            '<a href="#" class="morebutton">',
                this.moretext,
            '</a>'
        ].join('');
        if(!Ext.isEmpty(this.data)) {
            this._setTplAttrs(this.data);
        }

        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.morebutton',
            click: this._onMore
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.lessbutton',
            click: this._onLess
        });
        this.callParent(arguments);
    },

    _getMoreEl: function() {
        var element = Ext.get(this.getEl().query('.more')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },
    _getMoreButtonEl: function() {
        var element = Ext.get(this.getEl().query('a.morebutton')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },
    _getLessButtonEl: function() {
        var element = Ext.get(this.getEl().query('a.lessbutton')[0]);
        element.enableDisplayMode(); // Use css display instead of visibility for hiding.
        return element;
    },

    _onMore: function(e) {
        e.preventDefault();
        var button = this._getMoreButtonEl();
        this.moretext = button.getHTML();
        button.setHTML(this.lesstext);
        this._getMoreEl().show();
        Ext.defer(function() {
            // NOTE: We defer for two reasons: 1, prevent double click, 2: Prevent double event trigger (both more and less)
            button.replaceCls('morebutton', 'lessbutton');
        }, 200, this);
    },

    _onLess: function(e) {
        e.preventDefault();
        this._getMoreEl().hide();
        var button = this._getLessButtonEl();
        button.setHTML(this.moretext);
        Ext.defer(function() {
            // NOTE: We defer for two reasons: 1, prevent double click, 2: Prevent double event trigger (both more and less)
            button.replaceCls('lessbutton', 'morebutton');
        }, 200, this);
    },

    _setTplAttrs: function(data) {
        data.MORE_BUTTON = this.morebutton;
        data.MORE_ATTRS = 'class="more" style="display: none;"'
    },

    update: function(data) {
        this._setTplAttrs(data);
        return this.callParent([data]);
    }
});
