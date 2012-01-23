Ext.define('subjectadmin.view.action.List' ,{
    extend: 'Ext.Component',
    alias: 'widget.actionlist',
    cls: 'actionlist',

    /**
     * @cfg
     * 
     */
    links: [],

    tpl: [
        '<h2>{title}</h2>',
        '<ul>',
        '    <tpl for="links">',
        '       <li>',
        '           <a href="{url}" class="btn large primary">{text}</a>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ]
});
