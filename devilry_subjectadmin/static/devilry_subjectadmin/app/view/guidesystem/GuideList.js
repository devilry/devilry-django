Ext.define('devilry_subjectadmin.view.guidesystem.GuideList', {
    extend: 'Ext.Component',
    alias: 'widget.guidesystemlist',
    cls: 'devilry_subjectadmin_guidesystemlist bootstrap',

    /**
     * @cfg {Object[]} [guides]
     * Array of guides. Each item is an object with ``xtype``, ``title``, ``description`` attributes.
     */

    tpl: [
        '<tpl if="guides">',
            '<ul class="unstyled">',
                '<tpl for="guides">',
                    '<li><p>',
                        '<a href="#" data-guidextype="{xtype}" class="guide_link">',
                            '{title}',
                        '</a><br/>',
                        '<small class="muted">',
                            '{description}',
                        '</small>',
                    '</p></li>',
                '</tpl>',
            '</ul>',
        '</tpl>'
    ],

    initComponent: function() {
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.guide_link',
            click: this._onGuideClick
        });
        this.data = {
            guides: this.guides
        };
        this.callParent(arguments);
    },

    _onGuideClick: function(e) {
        e.preventDefault();
        var element = Ext.get(e.target);
        var xtype = element.getAttribute('data-guidextype');
        this.fireEvent('guideclick', this, xtype);
    }
});
