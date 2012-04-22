Ext.define('devilry_subjectadmin.view.shortcut.List', {
    extend: 'Ext.Component',
    alias: 'widget.shortcutlist',
    cls: 'shortcutlist',

    tpl: new Ext.XTemplate([
        '<ul>',
        '    <tpl for="items">',
        '       <li>',
        '           <a class="subjectlink" href="#/{subject}/">{subject}</a>',
        '           <ul>',
        '               <li><a class="btn btn-primary" href="#">Add assignment</a></li>',
        '               <tpl for="assignments">',
        '                   <li class="shortcut-list-item">',
        '                       <a class="assignmentlink" href="#/{subject}/{period}/{assignment}/">{displayName}</a>',
        '                   </li>',
        '               </tpl>',
        '           </ul>',
        '       </li>',
        '    </tpl>',
        '<ul>'
    ])
});
