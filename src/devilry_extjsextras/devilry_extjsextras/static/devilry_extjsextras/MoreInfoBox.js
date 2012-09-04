Ext.define('devilry_extjsextras.MoreInfoBox', {
    extend: 'Ext.container.Container',
    alias: 'widget.moreinfobox',

    /**
     * @cfg {string} [collapsedCls="muted"]
     * Class to add to ``intro`` and "More info"-link when collapsed.
     */
    collapsedCls: 'muted',

    /**
     * @cfg {String} [expandedCls=null]
     * Class to add to ``intro`` and "Less info"-link when expanded.
     */
    expandedCls: null,

    /**
     * @cfg {String} [introtext]
     * A single sentence to show as the intro. Always end it with ``.``.
     */

    /**
     * @cfg {Object} [moreWidget]
     * Config for the more-widget. This is the element that is shown in
     * addition to ``intro`` when "More info" is clicked.
     * Note that the ``anchor`` attribute will be overwritten.
     */

    /**
     * @cfg {String} [moretext="More info"]
     * Text of the "More info"-link
     */
    moretext: gettext('More info ...'),

    /**
     * @cfg {String} [lesstext="More info"]
     * Text of the "More info"-link
     */
    lesstext: gettext('Less info'),
    
    constructor: function(config) {
        this.callParent([config]);
        this.addEvents(
            /** @event
             * Fired when the "More info" button is clicked.
             * @param box This moreinfobox.
             */
            'moreclick',

            /** @event
             * Fired when the "Less info" button is clicked.
             * @param box This moreinfobox.
             */
            'lessclick'
        );
    },

    initComponent: function() {
        var cls = 'devilry_extjsextras_moreinfobox bootstrap';
        if(this.cls) {
            cls = Ext.String.format('{0} {1}', cls, this.cls);
        }
        this.cls = cls;

        this.moreWidget.anchor = '100%';
        this.moreWidget.hidden = true;
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'box',
                cls: this.collapsedCls,
                itemId: 'introBox',
                anchor: '100%',
                tpl: [
                    '<p>',
                        '{introtext}',
                        ' <a href="#" class="more_button">',
                            '{moretext}',
                        '</a>',
                    '</p>'
                ],
                data: {
                    introtext: this.introtext,
                    moretext: this.moretext
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a.more_button',
                    click: this._onMore
                }
            }, this.moreWidget, {
                xtype: 'box',
                itemId: 'lessButton',
                cls: this.expandedCls,
                hidden: true,
                html: [
                    '<p><a href="#">',
                        this.lesstext,
                    '</a></p>'
                ].join(''),
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a',
                    click: this._onLess
                }
            }]
        });
        this.callParent(arguments);
    },

    _getMoreWidget: function() {
        return this.getComponent(1);
    },
    _getIntroBox: function() {
        return this.down('#introBox');
    },
    _getLessButton: function() {
        return this.down('#lessButton');
    },
    _getMoreButtonEl: function() {
        return Ext.get(this._getIntroBox().getEl().query('a.more_button')[0]);
    },

    _onMore: function(e) {
        e.preventDefault();
        this._getMoreButtonEl().hide();
        if(!Ext.isEmpty(this.collapsedCls)) {
            this._getIntroBox().removeCls(this.collapsedCls);
        }

        if(!Ext.isEmpty(this.expandedCls)) {
            this._getIntroBox().addCls(this.expandedCls);
        }
        this._getMoreWidget().show();
        this._getLessButton().show();
        this.fireEvent('moreclick', this)
    },

    _onLess: function(e) {
        e.preventDefault();
        this._getLessButton().hide();
        this._getMoreWidget().hide();
        if(!Ext.isEmpty(this.expandedCls)) {
            this._getIntroBox().removeCls(this.expandedCls);
        }

        this._getMoreButtonEl().show();
        if(!Ext.isEmpty(this.collapsedCls)) {
            this._getIntroBox().addCls(this.collapsedCls);
        }
        this.fireEvent('lessclick', this)
    }
});
