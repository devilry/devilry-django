Ext.define('subjectadmin.view.ActionList', {
    extend: 'Ext.Component',
    alias: 'widget.actionlist',
    cls: 'actionlist',

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
