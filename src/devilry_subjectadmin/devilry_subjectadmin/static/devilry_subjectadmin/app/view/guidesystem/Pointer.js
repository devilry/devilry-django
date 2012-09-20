Ext.define('devilry_subjectadmin.view.guidesystem.Pointer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.guidesystem_pointer',
    requires: [
        'Ext.fx.Animator'
    ],
    cls: 'devilry_subjectadmin_guidesystem_pointer',

    floating: true,

    width: 100,
    height: 100,
    border: false,
    hideMode: 'visibility',

    initComponent: function() {
        Ext.apply(this, {
            bodyStyle: 'background-color: transparent !important;',
            //bodyStyle: 'background-color: red !important;',
            style: 'background-color: transparent !important;',
            frame: false,
            shadow: false,
            layout: 'fit',
            tpl: '<img src="{staticurl}/devilry_theme/resources/hugearrow/hugearrow_left.png" border="0"/>',
            data: {
                staticurl: DevilrySettings.DEVILRY_STATIC_URL
            }
        });
        this.callParent(arguments);
    },


    stopPointAt: function() {
        this.hide();
    },
    pointAt: function(element) {
        this.show();
        var offset = this.getHeight() / 2;
        this.alignTo(element, 'r', [10, -offset]);
    }

    //_animatePointer: function() {
        //var originX = this.getPosition()[0];
        //this.animate({
            //duration: 3000,
            //iterations: 1,
            //easing: 'ease',
            //keyframes: {
                //0: {
                    //x: originX
                //},
                //80: {
                    //x: originX + 50
                //},
                //100: {
                    //x: originX
                //}
            //}
        //});
    //}
});
