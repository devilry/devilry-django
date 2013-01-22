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
    showHeading: false,
    noResultsMsgTpl: [
        '<small class="muted">',
            gettext('No results matching {search} found.'),
        '</small>'
    ],

    requires: [
        'Ext.XTemplate'
    ],

    constructor:function () {
        this.addEvents(
            /**
             * @event resultLinkClick
             * Fired when a link to a search result is clicked.
             */
            'resultLinkClick'
        );
        this.callParent(arguments);
    },

    initComponent: function() {
        var headingTpl = [];
        if(this.showHeading) {
            headingTpl = ['<h3>', this.heading, '</h3>'];
        }

        var typeNameMap = {
            core_node: gettext('Node'),
            core_subject: gettext('Subject'),
            core_period: gettext('Period'),
            core_assignment: gettext('Assignment'),
            core_assignmentgroup: gettext('Group')
        };

        var me = this;
        Ext.apply(this, {
            cls: Ext.String.format('{0} {1}', this.cls, this.extraCls),
            tpl: [
                headingTpl.join(''),
                '<ul class="unstyled search-results">',
                    '<tpl for=".">',
                        '<li class="single-result-wrapper">',
                            this.singleResultTpl.join(''),
                        '</li>',
                    '</tpl>',
                '</ul>',
                '<p class="no-searchresults-box" style="display: none;">',
                    // NOTE: We set the value of this when it is shown
                '</p>',
                '<p>',
                    '<a class="btn btn-primary btn-small more-searchresults-button" style="display: none;">',
                        // NOTE: We set the value of this when it is shown
                    '</a>',
                '</p>', {
                    getTypeName:function (type) {
                        return typeNameMap[type];
                    },
                    getUrl:function (values) {
                        return Ext.bind(me.getUrl, me)(values);
                    },
                    joinStringArray:function (arr) {
                        return arr.join(', ');
                    },
                    getResultLinkCls:function () {
                        return 'result-target-link';
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
        this.addListener({
            scope: this,
            element: 'el',
            delegate: 'a.result-target-link',
            click: this._onResultLinkClick
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

    _getElement:function (cssselector) {
        var morebutton = Ext.get(this.getEl().query(cssselector)[0]);
        morebutton.enableDisplayMode();
        return morebutton;
    },

    _getMoreButton:function () {
        return this._getElement('.more-searchresults-button');
    },

    _getNoResultsBox:function () {
        return this._getElement('.no-searchresults-box');
    },

    _onSearchSuccess:function () {
        var store = this.getStore();
        if(store.getCount() <= this.loadCountDefault && store.getTotalCount() > store.getCount()) {
            this._onMoreResultsAvailable();
        }
        if(store.getCount() === 0) {
            this._onNoSearchResults();
        }
    },

    _onMoreResultsAvailable:function () {
        var store = this.getStore();
        var morebutton = this._getMoreButton();
        var loadcount = Ext.Array.min([store.getTotalCount(), this.loadCountMax]);
        morebutton.setHTML(interpolate(gettext('Load %(loadcount)s more'), {
            loadcount: loadcount
        }, true));
        morebutton.show();
    },

    _onNoSearchResults:function () {
        var box = this._getNoResultsBox();
        box.setHTML(Ext.create('Ext.XTemplate', this.noResultsMsgTpl).apply({
            search: Ext.String.format('<em>{0}</em>', this.currentSearch)
        }));
        box.show();
    },

    _onMore:function (e) {
        e.preventDefault();
        this._search({
            limit: this.loadCountMax
        });
    },

    _renderResult:function (unused, unused2, record) {
        return this.resultTplCompiled.apply(record.data);
    },

    getUrl:function (values) {
        return '#';
    },

    _onResultLinkClick:function (e) {
        this.fireEvent('resultLinkClick');
        // NOTE: We do not prevent the default action, so this does not prevent the link from
        //       triggering navigation.
    }
});