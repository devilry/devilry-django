/**
Devilry header version2 compatibility layer for the ExtJS apps. Renders as an empty
block of height 40px - this makes room for the header. The header is included in the 
header-block of the apptemplate, and is not removed when the viewport renders.
*/
Ext.define('devilry_header.Header2', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader2',
    margin: '0 0 0 0',
    height: 40, // NOTE: Make sure to adjust to the height of the actual devilry_header2

    requires: [
        'devilry_header.Breadcrumbs'
    ],

    /**
     * @cfg {string} [navclass]
     * The css class to style the header buttons with.
     */

    /**
     * @cfg {Object} [breadcrumbs=devilry_header.Breadcrumbs]
     * The object to use for breadcrumbs. You can also set this after load with #setBreadcrumbComponent.
     * Defaults to an instance of devilry_header.Breadcrumbs.
     */

    constructor: function(config) {
        config.cls = 'devilry_header2_extjsplaceholder';
        this.breadcrumbWrapper = Ext.widget('container', {
            cls: 'devilry_header2_breadcrumbwrapper'
        });
        this.callParent(arguments);
        this.setNavClass(config.navclass);
    },

    initComponent: function() {
        var breadcrumbareaItem;
        if(this.breadcrumbs) {
            breadcrumbareaItem = this.breadcrumbs;
        } else {
            breadcrumbareaItem = Ext.widget('breadcrumbs');
        }
        this.callParent(arguments);
    },

    setNavClass: function(navclass) {
        this.navclass = navclass;
        headerel = Ext.get('devilry_header2');
        headerel.addCls(Ext.String.format('devilry_header2_role_{0}', navclass));
    },

    setBreadcrumbComponent: function(config) {
        this.breadcrumbWrapper.removeAll();
        this.breadcrumbWrapper.add(config);
    },
});