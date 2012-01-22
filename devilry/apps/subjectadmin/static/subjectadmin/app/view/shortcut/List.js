Ext.define('subjectadmin.view.shortcut.List' ,{
    extend: 'Ext.Component',
    alias: 'widget.shortcutlist',
    store: 'ActiveAssignments',
    cls: 'shortcutlist',

    tpl: new Ext.XTemplate([
        '<h2>Shortcuts:</h2>',
        '<ul>',
        '    <tpl for="items">',
        '       <li>',
        '           <h3>{subject}</h3>',
        '           <ul>',
        '           <tpl for="assignments">',
        '               <li class="shortcut-list-item">',
        '                   <a href="#">{displayName}</a>',
        '               </li>',
        '           </tpl>',
        '           </ul>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ])
});
