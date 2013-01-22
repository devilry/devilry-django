Ext.define('devilry_header.BaseSearchResultsView', {
    extend: 'Ext.view.View',
    cls: 'devilry_header_searchresults bootstrap',

    /**
     * @cfg {string|string[]} [singleResultTpl]
     * The XTemplate for a single search result.
     */

    /**
     * @cfg {string} [heading=undefined]
     * The heading of the search result. Title is not shown if this is not defined.
     */

    hidden: true, // We show ourself automatically on search results
    loadCountDefault: 10,
    loadCountMax: 150,

    initComponent: function() {
        var headingTpl = [];
        if(!Ext.isEmpty(this.heading)) {
            headingTpl = ['<h3>', this.heading, '<h3>'];
        }

        var typeNameMap = {
            core_node: gettext('Node'),
            core_subject: gettext('Subject'),
            core_period: gettext('Period'),
            core_assignment: gettext('Assignment'),
            core_assignmentgroup: gettext('Group')
        };
        Ext.apply(this, {
            cls: Ext.String.format('{0} {1}', this.cls, this.extraCls),
            tpl: [
                headingTpl.join(''),
                '<ul class="unstyled">',
                    '<tpl for=".">',
                        '<li class="single-result-wrapper">',
                            this.singleResultTpl.join(''),
                        '</li>',
                    '</tpl>',
                '</ul>',
                '<p>',
                    '<a class="btn btn-primary btn-small more-searchresults-button" style="display: none;">',
                        // NOTE: We set the value of this when it is shown
                    '</a>',
                '</p>', {
                    getTypeName:function (type) {
                        return typeNameMap[type];
                    }
                }
            ],
            itemSelector: 'ul li.single-result-wrapper'
        });
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.more-searchresults-button',
            click: this._onMore
        });
        this.callParent(arguments);
    },

    _search:function (config) {
        this.getStore().search(Ext.apply({
            search: this.currentSearch
        }, config), {
            scope: this,
            callback:function (records, op) {
                if(op.success) {
                    this._onSearchSuccess();
                }
            }
        });
    },

    search:function (search) {
        this.show();
        this.currentSearch = search;
        this._search({
            limit: this.loadCountDefault
        });
    },

    _getMoreButton:function () {
        var morebutton = Ext.get(this.getEl().query('.more-searchresults-button')[0]);
        morebutton.enableDisplayMode();
        return morebutton;
    },

    _onSearchSuccess:function () {
        var store = this.getStore();
        if(store.getCount() <= this.loadCountDefault && store.getTotalCount() > store.getCount()) {
            var morebutton = this._getMoreButton();
            var loadcount = Ext.Array.min([store.getTotalCount(), this.loadCountMax]);
            morebutton.setHTML(interpolate(gettext('Load %(loadcount)s more'), {
                loadcount: loadcount
            }, true));
            morebutton.show();
        }
    },

    _onMore:function (e) {
        e.preventDefault();
        this._search({
            limit: this.loadCountMax
        });
    },

    _renderResult:function (unused, unused2, record) {
        return this.resultTplCompiled.apply(record.data);
    }
});