/**
Devilry header version2 compatibility layer for the ExtJS apps. Renders as an empty
block of height 70px - this makes room for the header. The header is included in the 
header-block of the apptemplate, and is not removed when the viewport renders.
*/
Ext.define('devilry_header.Header2', {
    extend: 'Ext.container.Container',
    alias: 'widget.devilryheader2',
    margin: '0 0 0 0',

    // NOTE: Make sure to adjust to the height of the height of
    // the .devilry_header2_extjs css class, plus room for the shadow.
    height: 42,
    heightWithoutBreadcrumb: 42,
    heightWithBreadcrumb: 72,

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
        this.headerel = Ext.get('devilry_header2');
        this.callParent(arguments);
        this.setNavClass(config.navclass);
    },

    initComponent: function() {
        this.callParent(arguments);

        var breadcrumbareaItem;
        if(this.breadcrumbs) {
            breadcrumbareaItem = this.breadcrumbs;
        } else {
            breadcrumbareaItem = Ext.widget('breadcrumbs');
        }
        this._setBreadcrumbComponent(breadcrumbareaItem);
    },

    setNavClass: function(navclass) {
        this.navclass = navclass;
        this.headerel.addCls(Ext.String.format('devilry_header2_role_{0}', navclass));
    },

    _setBreadcrumbComponent: function(breadcrumbareaItem) {
        var breadcrumbWrapper = Ext.widget('container', {
            cls: 'devilry_header2_breadcrumbwrapper'
        });
        breadcrumbWrapper.add(breadcrumbareaItem);
        var breadcrumbElement = Ext.get('devilry_header2_extjsbreadcrumb');
        breadcrumbWrapper.render(breadcrumbElement);
    },

    /*
    Used by devilry_header.Breadcrumbs, not for external use!
    */
    resizeHeaderForBreadcrumbs: function() {
        this.setHeight(this.heightWithBreadcrumb);
        this.headerel.addCls('devilry_header2_extjs_with_breadcrumb');
    },

    /*
    Used by devilry_header.Breadcrumbs, not for external use!
    */
    resizeHeaderForNoBreadcrumbs: function() {
        this.setHeight(this.heightWithoutBreadcrumb);
        this.headerel.removeCls('devilry_header2_extjs_with_breadcrumb');
    }
});