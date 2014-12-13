/**
 * A component for information display. Works just like a regular component,
 * except that it adds an extra attribute, ``MORE_BUTTON``, to the template
 * data. This extra attribute, inserts a button in the markup that toggles
 * the visibility of any element in the component with the ``.more`` css class.
 *
 * ## Example:
 *      {
 *          xtype: 'markupmoreinfobox',
 *          tpl: [
 *              'Always visible {MORE_BUTTON}',
 *              '<p {MORE_ATTRS}>Shown when more button is clicked.</p>'
 *          ],
 *          data: {}
 *      }
 *
 * **Note**: we use {MORE_ATTRS}, which simply inserts ``class="more" style="display: none;"``.
 *
 * ## Special template attributes
 *
 * - ``MORE_BUTTON``: The more button (an A-tag).
 * - ``MORE_ATTRS``: The html attributes required on a container for the
 *   more/less buttons show/hide the container. The value is:
 *   ``class="more" style="display: none;"``. If you set the
 *   ``moreCls`` config, that/those classes are added to ``class``.
 */
Ext.define('devilry_extjsextras.MarkupMoreInfoBox', {
    extend: 'Ext.Component',
    alias: 'widget.markupmoreinfobox',
    border: false,
    frame: false,

    /**
     * @cfg {String} [cls="markupmoreinfobox"]
     * Defaults to ``markupmoreinfobox bootstrap``.
     */
    cls: 'markupmoreinfobox bootstrap',

    /**
     * @cfg {String} [lesstext="Less info"]
     * The text to show on the Less info button. The default text is translated.
     */
    lesstext: gettext('Less info'),

    /**
     * @cfg {String} [lesstext="More info ..."]
     * The text to show on the More info button. The default text is translated.
     */
    moretext: gettext('More info'),

    moresuffix: '<span class="expandable-indicator"></span>',
    lesssuffix: '<span class="collapsible-indicator"></span>',

    /**
     * @cfg {String} [moreCls='']
     * Added to the ``class`` attribute of the ``MORE_ATTRS`` template variable.
     */
    moreCls: '',

    initComponent: function() {
        this.morebutton = [
            '<a href="#" class="morebutton">',
                this.moretext, this.moresuffix,
            '</a>'
        ].join('');
        if(!Ext.isEmpty(this.data)) {
            this.setTplAttrs(this.data);
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
        button.setHTML(this.lesstext + this.lesssuffix);
        this._getMoreEl().show();
        this.hide(); this.show(); // Force re-render
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
        this.hide(); this.show(); // Force re-render
        Ext.defer(function() {
            // NOTE: We defer for two reasons: 1, prevent double click, 2: Prevent double event trigger (both more and less)
            button.replaceCls('lessbutton', 'morebutton');
        }, 200, this);
    },

    setTplAttrs: function(data) {
        data.MORE_BUTTON = this.morebutton;
        data.MORE_ATTRS = Ext.String.format('class="more {0}" style="display: none;"', this.moreCls);
        data.MORE_STYLE = 'style="display: none;"';
    },

    update: function(data) {
        this.setTplAttrs(data);
        return this.callParent([data]);
    }
});
