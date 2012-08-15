Ext.define('devilry_student.view.add_delivery.AddDeliveryPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.add_delivery',
    margin: '40 20 20 20',

    requires: [
        'Ext.util.Cookies'
    ],

    /**
     * @cfg {Object} [groupInfoRecord]
     */

    metaTpl: [
        '<h3>', gettext('Uploaded files'), '</h3>',
        '<p>TODO</p>'
    ],

    helptextTpl: [
        '<tpl if="created">',
            '<p><strong>', gettext('File uploaded successfully'), '<strong></p>',
            '<p>', gettext('Click the Deliver-button to deliver these {filenameCount} files, or choose <em>Add new file</em> to upload more files.'), '</p>',
        '<tpl else>',
            '<p>', gettext('Upload files for your {delivery_term}. You can upload multiple files.'), '</p>',
        '</tpl>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            ui: 'inset-header-panel',
            cls: 'devilry_student_groupinfo_add_delivery',
            title: interpolate(gettext('Add %(delivery_term)s'), {
                delivery_term: gettext('delivery'),
            }, true),
            layout: 'column',
            items: [{
                xtype: 'form',
                border: false,
                columnWidth: 0.7,
                layout: 'anchor',
                items: [{
                    xtype: 'box',
                    tpl: this.helptextTpl,
                    itemid: 'help',
                    anchor: '100%', // anchor width by percentage
                    cls: 'bootstrap devilry_student_groupinfo_add_delivery_help',
                    data: {
                        created: false,
                        delivery_term: gettext('delivery')
                    }
                }, {
                    xtype: 'hidden',
                    name: 'delivery_id',
                    value: ''
                }, {
                    xtype: 'hidden',
                    name: 'finish',
                    value: ''
                }, {
                    xtype: 'hidden',
                    name: 'csrfmiddlewaretoken',
                    value: Ext.util.Cookies.get('csrftoken')
                }, {
                    xtype: 'fileuploadfield',
                    name: 'file_to_add',
                    hideLabel: true,
                    allowBlank: true,
                    anchor: '100%', // anchor width by percentage
                    emptyText: gettext('Select file...'),
                    buttonText: gettext('Add new file')
                }]
            }, {
                columnWidth: 0.3,
                xtype: 'box',
                cls: 'bootstrap devilry_student_groupinfo_add_delivery_meta',
                itemId: 'meta',
                padding: '0 0 0 40',
                tpl: this.metaTpl,
                data: {
                }
            }]
        });
        this.callParent(arguments);
    }
});
