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
                    '<button class="btn btn-primary previous-searchresult-button">',
                        '<i class="icon-white icon-chevron-left"></i>',
                    '</button>',
                    '<button class="btn btn-primary next-searchresult-button">',
                        '<i class="icon-white icon-chevron-right"></i>',
                    '</button>',
                '</p>', {
                    getTypeName:function (type) {
                        return typeNameMap[type];
                    }
                }
            ],
            itemSelector: 'ul li.single-result-wrapper'
        });
        this.callParent(arguments);
    },

    search:function (search) {
        this.show();
        this.getStore().search({
            search: search
        }, {
            callback:function (records, op) {
                if(op.success) {
                }
            }
        });
    },

    _renderResult:function (unused, unused2, record) {
        return this.resultTplCompiled.apply(record.data);
    }
});