Ext.define('subjectadmin.view.shortcut.List' ,{
    extend: 'Ext.Component',
    alias: 'widget.shortcutlist',
    cls: 'shortcutlist',

    tpl: new Ext.XTemplate([
        '<h2>Shortcuts:</h2>',
        '<ul>',
        '    <tpl for="items">',
        '       <li>',
        '           <a href="#/{subject}">{subject}</a>',
        '           <ul>',
        '           <tpl for="assignments">',
        '               <li class="shortcut-list-item">',
        '                   <a href="#/{subject}/{period}/{assignment}">{displayName}</a>',
        '               </li>',
        '           </tpl>',
        '           </ul>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ])
});
