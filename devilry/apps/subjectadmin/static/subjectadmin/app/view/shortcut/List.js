Ext.define('subjectadmin.view.shortcut.List' ,{
    extend: 'Ext.Component',
    alias: 'widget.shortcutlist',
    cls: 'shortcutlist bootstrap',

    tpl: new Ext.XTemplate([
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
