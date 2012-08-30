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
            '<p>', gettext('Click the <em>Submit {delivery_term}</em> button to deliver these {filenameCount} files, or choose <em>Add new file</em> to upload more files.'), '</p>',
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
            }
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
                    xtype: 'box',
                    hidden: !this._isLinuxFirefox14(),
                    cls: 'alert alert-warn',
                    html: [
                        '<h3>Known issue with your browser</h3>',
                        '<p>',
                            'The Firefox version running on UiO linux machines, has a problem with the file upload button below. You should be able to press the lower 3 or 4 pixels of the button. If not, please use another machine and operating system to make your deliveries while we fix this issue. ',
                            'See <a href="https://github.com/devilry/devilry-django/issues/293" target="_blank">issue #293</a> for more info.',
                        '</p>'
                    ].join('')
                //}, {
                    //xtype: 'fileuploadfield',
                    //name: 'file_to_add',
                    //hideLabel: true,
                    //allowBlank: true,
                    //anchor: '100%', // anchor width by percentage
                    //emptyText: gettext('Select file...'),
                    //buttonText: gettext('Add new file')
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
    },

    _isLinuxFirefox14: function() {
        return Ext.is.Linux && Ext.firefoxVersion >= 10;
    }
});
