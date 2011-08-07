Ext.define('devilry.administrator.node.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_nodeprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<section class="help">',
        '    <h1>What is a node?</h1>',
        '    <p>',
        '        A Node is a place to organise top-level administrators (administrators responsible for more than one subject).',
        '        Nodes are organised in a tree. This is very flexible, and can be used to emulate most administrative hierarchies.',
        '    </p>',
        '</section>'
    )
});
