/**
 * Defines a menu of actions (urls).
 * */
Ext.define('subjectadmin.view.ActionList', {
    extend: 'Ext.Component',
    alias: 'widget.actionlist',
    cls: 'actionlist box',

    tpl: [
        '<h2 class="boxtitle">{title}</h2>',
        '<ul class="boxbody">',
        '    <tpl for="links">',
        '       <li>',
        '           <a href="{url}" class="btn large {buttonType}">{text}</a>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ],


    /**
     * @cfg {String} title (required)
     */

    /**
     * @cfg {[Object]} links (required)
     *
     * Each object should define an ``url``, ``text`` and optional ``buttonType``.
     *
     * ``buttonType`` defaults to "primary". Other possible values: "danger".
     */

    initComponent: function() {
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
