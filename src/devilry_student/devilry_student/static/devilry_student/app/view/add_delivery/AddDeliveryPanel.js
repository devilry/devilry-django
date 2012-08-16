Ext.define('devilry_student.view.add_delivery.AddDeliveryPanel' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.add_delivery',
    margin: '20 20 20 20',

    requires: [
        'Ext.util.Cookies'
    ],

    /**
     * @cfg {Object} [groupInfoRecord]
     */

    metaTpl: [
        '<tpl if="uploadedfiles">',
            '<h3>', gettext('Uploaded files'), '</h3>',
            '<ul>',
                '<tpl for="uploadedfiles">',
                    '<li>{filename}</li>',
                '</tpl>',
            '</ul>',
        '</tpl>'
    ],

    helptextTpl: [
        '<h2>',
            interpolate(gettext('Add %(delivery_term)s'), {
                delivery_term: gettext('delivery'),
            }, true),
        '</h2>',
        '<tpl if="added_filename">',
            '<p><strong>', gettext('{added_filename} uploaded successfully'), '</strong></p>',
            '<p>', gettext('Click the <em>Submit {delivery_term}</em> button to deliver these {filenameCount} files, or choose <em>Add new file</em> to upload more files.'), '</p>',
        '<tpl else>',
            '<p>', gettext('Upload files for your {delivery_term}. You can upload multiple files.'), '</p>',
        '</tpl>'
    ],

    initComponent: function() {
        Ext.apply(this, {
            cls: 'devilry_student_groupinfo_add_delivery',
            layout: 'column',
            items: [{
                xtype: 'form',
                border: false,
                columnWidth: 0.7,
                layout: 'anchor',
                items: [{
                    xtype: 'box',
                    tpl: this.helptextTpl,
                    itemId: 'help',
                    anchor: '100%', // anchor width by percentage
                    cls: 'bootstrap devilry_student_groupinfo_add_delivery_help',
                    data: {
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
                }],
                dockedItems: [{
                    xtype: 'toolbar',
                    margin: '20 0 0 0',
                    dock: 'bottom',
                    ui: 'footer',
                    items: [{
                        xtype: 'button',
                        itemId: 'cancelbutton',
                        text: gettext('Cancel')
                    }, '->', {
                        xtype: 'button',
                        itemId: 'deliverbutton',
                        scale: 'large',
                        disabled: true,
                        text: interpolate(gettext('Submit %(delivery_term)s'), {
                            delivery_term: gettext('delivery')
                        }, true)
                    }]
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
