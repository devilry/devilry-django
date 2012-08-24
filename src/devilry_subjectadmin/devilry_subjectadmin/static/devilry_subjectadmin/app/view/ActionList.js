/**
 * Defines a menu of actions (urls).
 * */
Ext.define('devilry_subjectadmin.view.ActionList', {
    extend: 'Ext.Component',
    alias: 'widget.actionlist',
    cls: 'devilry_subjectadmin_actionlist bootstrap',

    tpl: [
        '<ul>',
        '    <tpl for="links">',
        '       <li>',
        '           <strong><a href="{url}" style="{style}">{text}</a></strong>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ],

    /**
     * @cfg {[Object]} links (required)
     *
     * Each object should define an ``url``, ``text`` and optional ``buttonType``.
     *
     * ``buttonType`` defaults to "primary". Other possible values: "danger", "default".
     */

    /**
     * @cfg {string} linkStyle (optional)
     *
     * Css styles common to all links.
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
            } else if(link.buttonType == 'default') {
                link.buttonType = '';
            }
            if(link.buttonSize == undefined) {
                link.buttonSize = 'large'
            }
            link.style = this.linkStyle || '';
        }, this);
        this.data = {
            title: this.title,
            links: this.links
        }
        this.callParent(arguments);
    }
});
