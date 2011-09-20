/**
 * Panel for file upload.
 */
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
         * Id of the assignment group.
         */
        assignmentgroupid: undefined,

        /**
         * @cfg
         * Only used to display "Click to view" link. (optional)
         */
        agroup_recordcontainer: undefined,

        /**
         * @cfg
         * The name of the Delivery ``Ext.data.Model``.
         */
        deliverymodelname: undefined
    },

    uploadedFilesTpl: Ext.create('Ext.XTemplate',
        '<tpl if="deliverysuccessful">',
        '   <div class="section ok">',
        '       <h1>Success</h1>',
        '       <p>Delivery created.',
        '           <tpl if="agroup">',
        '               <a href="{DEVILRY_URLPATH_PREFIX}/student/assignmentgroup/{agroup.id}?deliveryid={delivery.id}">Click here</a> to view the delivery.',
        '           </tpl>',
        '       </p>',
        '   </section>',
        '</tpl>',
        '<tpl if="!deliverysuccessful">',
        '   <tpl if="filenames.length &gt; 0">',
        '      <div class="section info">',
        '          <h1>File uploaded successfully</h1>',
        '          <p>You have uploaded the following {filenames.length} files.</p>',
        '          <ul>',
        '          <tpl for="filenames">',
        '              <li>{.}</li>',
        '          </tpl>',
        '          </ul>',
        '          <p>Click the <span class="menuref">deliver</span> button to deliver these {filenames.length} files, or choose <span class="menuref">Add new file</span> to upload more files.</p>',
        '      </section>',
        '   </tpl>',
        '   <tpl if="filenames.length == 0">',
        '      <div class="section help">',
        '          <h1>Create delivery</h1>',
        '          <p>{initialhelptext}</p>',
        '      </section>',
        '   </tpl>',
        '</tpl>'
    ),

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        //this.uploadedFiles = ['HelloWorld.py', 'This is a test.txt', 'This-is-a-long-filename-loooooong.longstuff.java'];
        this.uploadedFiles = [];
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
                buttonText: 'Add new file',
                buttonConfig: {
                    scale: 'large'
                },
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
    },


    /**
     * @private
     */
    updateInfoBox: function(finished) {
        this.infoBoxView.update({
            filenames: this.uploadedFiles,
            initialhelptext: this.initialhelptext,
            deliverysuccessful: finished,
            delivery: (this.deliveryrecord? this.deliveryrecord.data: null),
            DEVILRY_URLPATH_PREFIX: DevilrySettings.DEVILRY_URLPATH_PREFIX,
            agroup: (this.agroup_recordcontainer.record? this.agroup_recordcontainer.record.data: null)
        });
    },



    /**
     * @private
     */
    createInitialDelivery: function() {
        this.getEl().mask('Initializing delivery...');
        var delivery = Ext.create(this.deliverymodelname, {
            deadline: this.deadlineid,
            id: null,
            successful: false
        });
        delivery.save({
            scope: this,
            success: this.onCreateDeliverySuccess,
            failure: this.onCreateDeliveryFailure
        });
    },

    /**
     * @private
     */
    onCreateDeliverySuccess: function(deliveryrecord) {
        this.deliveryrecord = deliveryrecord;
        this.getEl().unmask();
        this.uploadFileInForm();
    },

    /**
     * @private
     */
    onCreateDeliveryFailure: function(x) {
        this.getEl().unmask();
        Ext.Msg.alert('Error', 'Could not create delivery on the selected deadline.'); // TODO: Check status code for permission denied.
    },



    /**
     * @private
     */
    onAddFile: function () {
        if(!this.deliveryrecord) {
            this.createInitialDelivery();
        } else {
            this.uploadFileInForm();
        }
    },

    /**
     * @private
     */
    uploadFileInForm: function() {
        var form = this.getForm();
        var url = Ext.String.format(
            '{0}/student/add-delivery/fileupload/{1}',
            DevilrySettings.DEVILRY_URLPATH_PREFIX, this.assignmentgroupid
        );
        if(form.isValid()){
            form.submit({
                url: url,
                scope: this,
                params: {deliveryid: this.deliveryrecord.data.id},
                waitMsg: 'Uploading your file...',
                success: this.onAddFileSuccess,
                failure: this.onAddFileFailure
            });
        }
    },

    /**
     * @private
     */
    onAddFileSuccess: function(form, res) {
        this.uploadedFiles.push(res.result.file);
        this.updateInfoBox();
        this.deliverbutton.enable(); // really only needed on first upload, but it does not hurt.
    },

    /**
     * @private
     */
    onAddFileFailure: function(form, res) {
        Ext.Msg.alert('Failure', 'Error during upload, TRY AGAIN!');
    },



    /**
     * @private
     */
    onDeliver: function() {
        this.deliveryrecord.data.successful = true;
        this.getEl().mask('Saving...');
        this.deliveryrecord.save({
            scope: this,
            success: this.onDeliverSuccess,
            failure: this.onDeliverFailure
        });
    },

    /**
     * @private
     */
    onDeliverSuccess: function() {
        this.uploadedFiles = [];
        this.deliverbutton.disable();
        this.updateInfoBox(true);
        this.deliveryrecord = null;
        this.getEl().unmask();
    },

    /**
     * @private
     */
    onDeliverFailure: function() {
        this.getEl().unmask();
        Ext.Msg.alert('Failure', 'Error when finalizing the delivery, TRY AGAIN!');
    }
});
