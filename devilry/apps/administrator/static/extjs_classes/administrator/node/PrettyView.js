Ext.define('devilry.administrator.node.PrettyView', {
    extend: 'devilry.administrator.PrettyView',
    alias: 'widget.administrator_nodeprettyview',

    bodyTpl: Ext.create('Ext.XTemplate',
        '<div class="section help">',
        '    <h1>What is a node?</h1>',
        '    <p>',
        '        A Node is a place to organise top-level administrators (administrators responsible for more than one subject).',
        '        Nodes are organised in a tree. This is very flexible, and can be used to emulate most administrative hierarchies.',
        '    </p>',
        '   <h1>Usage</h1>',
        '   <p>Use the <span class="menuref">Active periods/semesters</span> to get an overview over the currently running periods, and if the administrators have registered which students qualify for final exams.</p>',
        '   <p>The <span class="menuref">Direct childnodes</span> and <span class="menuref">Subjects</span> tabs are lists of everything organized directly below this node.</p>',
        '</div>'
    ),

    initComponent: function() {
        if(this.record) {
            this._onLoadRecord();
        } else {
            this.on('loadmodel', this._onLoadRecord, this);
        }
        this.callParent(arguments);
    },

    _onLoadRecord: function() {
    }
});
