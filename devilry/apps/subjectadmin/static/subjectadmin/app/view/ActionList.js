/**
 * Defines a menu of actions (urls).
 * */
Ext.define('subjectadmin.view.ActionList', {
    extend: 'Ext.Component',
    alias: 'widget.actionlist',

    tpl: [
        '<ul class="boxbody">',
        '    <tpl for="links">',
        '       <li>',
        '           <a href="{url}" class="btn large {buttonType}">{text}</a>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ],

    /**
     * @cfg {[Object]} links (required)
     *
     * Each object should define an ``url``, ``text`` and optional ``buttonType``.
     *
     * ``buttonType`` defaults to "primary". Other possible values: "danger".
     */

    initComponent: function() {
        if(this.cls) {
            this.cls = this.cls + ' actionlist';
        } else {
            this.cls = 'actionlist'
        }
        Ext.Array.each(this.links, function(link) {
            if(link.buttonType == undefined) {
                link.buttonType = 'primary';
            }
        });
        this.data = {
            title: this.title,
            links: this.links
        }
        this.callParent(arguments);
    }
});
