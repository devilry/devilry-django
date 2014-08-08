Ext.define('devilry_nodeadmin.view.dashboard.BetaWarning', {
    extend: 'Ext.view.View',
    alias: 'widget.betawarning',
    cls: 'devilry_nodeadmin_betawarning bootstrap',
    tpl: [
        '<p class="muted">',
            gettext( 'This part of Devilry is in experemental stage. To make sure you get things done, we have kept a stable environment accessible, providing the same functionality. If you ever encounter issues with this page, please make sure to report them and head over  ' ),
            '<a href="/administrator">', gettext( 'to the alternative interface' ), '</a>.',
        '</p>'
    ],

    itemSelector: 'div',

    initComponent: function() {
        this.callParent(arguments);
    }
});
