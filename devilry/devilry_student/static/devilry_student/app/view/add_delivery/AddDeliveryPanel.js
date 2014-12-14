Ext.require([
    'Ext.layout.container.Column',
    'Ext.form.field.Hidden'
]);
Ext.define('devilry_student.view.add_delivery.AddDeliveryPanel' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.add_delivery',
    margin: '20 20 20 20',

    requires: [
        'Ext.util.Cookies',
        'devilry_extjsextras.PrimaryButton',
        'devilry_student.view.add_delivery.ConfirmAfterDeadline',
        'devilry_student.view.add_delivery.NativeFileUpload'
    ],

    /**
     * @cfg {Object} [groupInfoRecord]
     */

    metaTpl: [
        '<div class="uploadedfilesbox">',
            '<tpl if="uploadedfiles">',
                '<h3>', gettext('Uploaded files'), '</h3>',
                '<ul>',
                    '<tpl for="uploadedfiles">',
                        '<li>{filename}</li>',
                    '</tpl>',
                '</ul>',
            '</tpl>',
        '</div>'
    ],

    helptextTpl: [
        '<h2>',
            interpolate(gettext('Add %(delivery_term)s'), {
                delivery_term: gettext('delivery')
            }, true),
        '</h2>',
        '<tpl if="added_filename">',
            '<p><strong>', gettext('{added_filename} uploaded successfully'), '</strong></p>',
            '<p>', gettext('Click the <em>Submit {delivery_term}</em> button to deliver these {filenameCount} files, or upload more files.'), '</p>',
        '<tpl else>',
            '<p class="initial_text">', gettext('Upload files for your {delivery_term}. You can upload multiple files.'), '</p>',
        '</tpl>'
    ],

    initComponent: function() {
        var confirm_after_deadline = {
            xtype: 'box',
            cls: 'devilry_student_delivery_before_deadline',
            html: ''
        };
        if(this.groupInfoRecord.deadline_expired()) {
            confirm_after_deadline = {
                xtype: 'confirm_after_deadline'
            };
        }
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
                    cls: 'bootstrap add_delivery_help',
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
                    xtype: 'native_file_upload',
                    name: 'file_to_add',
                    allowBlank: true
                }, confirm_after_deadline],
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
                        xtype: 'primarybutton',
                        itemId: 'deliverbutton',
                        //scale: 'large',
                        minWidth: 200,
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
