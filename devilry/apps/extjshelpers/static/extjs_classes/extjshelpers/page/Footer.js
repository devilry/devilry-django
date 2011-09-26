Ext.define('devilry.extjshelpers.page.Footer', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.pagefooter',
    border: false,
    margins: '0 0 0 0',
    autoHeight: true,

    html: Ext.create('Ext.XTemplate',
        '<div class="footer">',
        '   <a href="http://devilry.org">Devilry</a> is an open source general purpose delivery system.',
        '</div>'
    ).apply({})
});
