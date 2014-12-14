/** A menu listing selected groups, and the ability to deselect them. */
Ext.define('devilry_subjectadmin.view.managestudents.SelectedGroupsMenu', {
    extend: 'Ext.menu.Menu',
    alias: 'widget.selectedgroupsmenu',
    cls: 'devilry_subjectadmin_selectedgroupsmenu',

    listingTpl: [
        '<tpl if="selectedGroupRecords">',
            '<p>',
                gettext('Selected groups'), ': ',
                '<tpl for="selectedGroupRecords">',
                    '<a href="#" class="selected_group" data-groupid="{data.id}">',
                        '{[this.getGroupIdentString(values)]}',
                    '</a>',
                    '<tpl if="xindex != xcount">',
                        ', ',
                    '</tpl>',
                '</tpl>',
                '.',
            '</p>',
            '<p class="muted"><small>(',
                gettext('click group to deselect it'),
            ')</small></p>',
        '</tpl>', {
            getGroupIdentString: function(groupRecord) {
                return Ext.String.ellipsis(groupRecord.getIdentString(), 20);
            }
        }
    ],

    /**
     * @cfg {Object} [grid]
     * The grid to show selection for.
     */

    initComponent: function() {
        Ext.apply(this, {
            plain: true,
            layout: 'fit',
            items: {
                xtype: 'box',
                cls: 'bootstrap',
                padding: 10,
                itemId: 'listingBox',
                tpl: this.listingTpl,
                style: 'white-space: normal !important;',
                data: {
                    selectedGroupRecords: null
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: 'a.selected_group',
                    click: function(e) {
                        e.preventDefault();
                        this._onClickGroup(e);
                    }
                }
            }
        });
        this.on({
            scope: this,
            beforeshow: this._onBeforeShow
        });
        this.callParent(arguments);
    },

    _onBeforeShow: function() {
        this._refreshListingBox();
    },

    _refreshListingBox: function() {
        var selectedGroupRecords = this.grid.getSelectionModel().getSelection();
        this.setWidth(this.grid.getWidth() - 10);
        this.down('#listingBox').update({
            selectedGroupRecords: selectedGroupRecords
        });
    },

    _onClickGroup: function(e) {
        var element = Ext.get(e.target);
        var id = parseInt(element.getAttribute('data-groupid'), 10);
        var groupRecord = this._getGroupRecordById(id);
        var selModel = this.grid.getSelectionModel();
        selModel.deselect([groupRecord]);
        if(selModel.getSelection().length === 0) {
            this.hide();
        } else {
            this._refreshListingBox();
        }
    },

    _getGroupRecordById: function(groupId) {
        var store = this.grid.getStore();
        var index = store.findExact('id', groupId);
        if(index == -1) {
            return undefined;
        }
        return store.getAt(index);
    }
});
