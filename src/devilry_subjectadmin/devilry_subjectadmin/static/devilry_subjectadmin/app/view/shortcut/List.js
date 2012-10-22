Ext.define('devilry_subjectadmin.view.shortcut.List', {
    extend: 'Ext.Component',
    alias: 'widget.shortcutlist',
    cls: 'shortcutlist',

    tpl: new Ext.XTemplate([
        '<p>',
        gettext('Active your courses are shown below.'),
        '</p>',
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
        '<ul>',
        '<p>',
            '<a href="#/" class="btn">',
                gettext('Browse all your subjects (including old/archived)'),
            '<a>',
        '</p>'
    ])
});
