Ext.define('devilry.statistics.PeriodAdminLayout', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.statistics-periodadminlayout', // NOTE: devilry.statistics.sidebarplugin.qualifiesforexam.Manual depends on this alias
    layout: 'fit',
    requires: [
        'devilry.statistics.Loader',
        'devilry.statistics.SidebarPluginContainer',
        'devilry.statistics.dataview.DataView',
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main',
        'devilry.statistics.OverviewOfSingleStudent'
    ],

    /**
     * @cfg
     */
    periodid: undefined,

    /**
     * @cfg
     */
    defaultViewClsname: 'devilry.statistics.dataview.FullGridView',

    /**
     * @cfg
     */
    hidesidebar: false,

    sidebarplugins: [
        'devilry.statistics.sidebarplugin.qualifiesforexam.Main'
    ],

    titleTpl: Ext.create('Ext.XTemplate',
        '{parentnode__long_name:ellipsis(60)} &mdash; {long_name}'
    ),

    constructor: function() {
        this.callParent(arguments);
    },
    
    initComponent: function() {
        this._isLoaded = false;
        Ext.apply(this, {
            items: [],
            frame: false,
            border: false
        });
        this.on('afterrender', this._onAfterRender, this);
        this.callParent(arguments);
    },

    loadIfNotLoaded: function() {
        if(!this._isLoaded) {
            this._isLoaded = true;
            this._loadStudents();
        }
    },

    _loadStudents: function() {
        Ext.create('devilry.statistics.Loader', this.periodid, {
            listeners: {
                scope: this,
                minimalDatasetLoaded: this._onMinimalDatasetLoaded,
                mask: this._onMask,
                unmask: this._onUnmask
            }
        });
    },

    _onAfterRender: function() {
        Ext.defer(function() {
            this._rendered = true;
            if(this._unappliedMask) {
                this._mask(this._unappliedMask);
                this._unappliedMask = null;
            }
        }, 100, this);
    },
    _onMask: function(loader, msg) {
        if(this._rendered) {
            this._mask(msg);
        } else {
            this._unappliedMask = msg;
        }
    },
    _onUnmask: function() {
        this._unappliedMask = null;
        if(this._rendered) {
            this._unmask();
        }
    },
    _mask: function(msg) {
        this.getEl().mask(msg);
    },
    _unmask: function() {
        this.getEl().unmask();
    },

    _onMinimalDatasetLoaded: function(loader) {
        var title = this.titleTpl.apply(loader.periodRecord.data);
        this.removeAll();
        this.add({
            xtype: 'panel',
            border: false,
            frame: false,
            layout: 'border',
            items: [{
                xtype: 'statistics-sidebarplugincontainer',
                title: 'Label students',
                region: 'east',
                collapsible: true,
                collapsed: this.hidesidebar,
                width: 350,
                autoScroll: true,
                loader: loader,
                sidebarplugins: this.sidebarplugins
            }, this._dataview = Ext.widget('statistics-dataview', {
                defaultViewClsname: this.defaultViewClsname,
                region: 'center',
                loader: loader
            })]
        });
    }
});
