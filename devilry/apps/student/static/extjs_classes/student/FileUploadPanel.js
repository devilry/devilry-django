Ext.define('devilry.student.FileUploadPanel', {
    extend: 'Ext.form.Panel',
    alias: 'widget.fileuploadpanel',
    cls: 'widget-fileuploadpanel',

    config: {
        /**
         * @cfg
         * A help text to show with the upload field.
         */
        initialhelptext: undefined,

        /**
         * @cfg
         * Id of the deadline.
         */
        deadlineid: undefined,

        /**
         * @cfg
         * Id of the delivery.
         */
        deliveryid: undefined
    },

    uploadedFilesTpl: Ext.create('Ext.XTemplate',
        '<tpl if="filenames.length &gt; 0">',
        '   <section class="ok">',
        '         <h1>Success!</h1>',
        '         <p>You have uploaded the following {filenames.length} files.</p>',
        '         <ul>',
        '         <tpl for="filenames">',
        '             <li>{.}</li>',
        '         </tpl>',
        '         </ul>',
        '         <p>Click the <span class="menuref">deliver</span> button to deliver these {filenames.length} files, or upload more files.',
        '   </section>',
        '</tpl>',
        '<tpl if="filenames.length == 0">',
        '   <section class="help">',
        '         <h1>Create delivery</h1>',
        '         <p>{initialhelptext}</p>',
        '   </section>',
        '</tpl>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        this.uploadedFiles = ['HelloWorld.py', 'This is a test.txt', 'This-is-a-long-filename-loooooong.longstuff.java'];
        this.infoBoxView = Ext.widget('box', {
            tpl: this.uploadedFilesTpl,
        });
        this.updateInfoBox();

        this.deliverbutton = Ext.widget('button', {
            text: 'Deliver!',
            scale: 'large',
            disabled: true,
            listeners: {
                scope: this,
                click: this.onDeliver
            }
        });

        Ext.apply(this, {
            items: [this.infoBoxView, {
                xtype: 'fileuploadfield',
                name: 'uploaded_file',
                fieldLabel: 'Delivery',
                hideLabel: true,
                labelWidth: 50,
                width: '100%',
                anchor: '100%',
                msgTarget: 'side',
                allowBlank: true,
                emptyText: 'Select file...',
                buttonText: 'Browse...',
                listeners: {
                    scope: this,
                    change: this.onAddFile
                }
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', this.deliverbutton]
            }]
        });
        this.callParent(arguments);
        this.addListener('render', function() {
            if(this.deliveryid == undefined) {
                this.getEl().mask('Loading');
            }
        }, this);
    },

    enableDeliveries: function(deliveryid) {
        this.setDeliveryid(deliveryid);
        if(this.rendered) {
            this.getEl().unmask();
        }
    },

    updateInfoBox: function() {
        this.infoBoxView.update({
            filenames: this.uploadedFiles,
            initialhelptext: this.initialhelptext
        });
    },

    onAddFile: function () {
        var form = this.getForm();
        var url = Ext.String.format(
            '{0}/student/add-delivery/fileupload/{1}',
            DevilrySettings.DEVILRY_MAIN_PAGE, this.deadlineid
        );
        if(form.isValid()){
            form.submit({
                url: url,
                scope: this,
                params: {deliveryid: this.deliveryid},
                waitMsg: 'Uploading your file...',
                success: this.onAddFileSuccess,
                failure: this.onAddFileFailure
            });
        }
    },

    onAddFileSuccess: function(form, res) {
        //var successMsg = Ext.String.format(
            //'File {0} has been uploaded (to delivery {1}).\nSelect another file for upload',
            //res.result.file, res.result.deliveryid
        //);
        //Ext.Msg.alert('Success', successMsg);
        this.uploadedFiles.push(res.result.file);
        this.updateInfoBox();
        this.deliverbutton.enable(); // really only needed on first upload, but it does not hurt.
    },

    onAddFileFailure: function(form, res) {
        Ext.Msg.alert('Failure', 'Error during upload, TRY AGAIN!');
    },

    onDeliver: function() {
        console.log('Deliver');
    }
});
