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
        deliverymodelname: undefined,

        /**
         * @cfg
         * Filenames are added to this store on each upload.
         */
        uploadedFilesStore: undefined
    },

    uploadedFilesTpl: Ext.create('Ext.XTemplate',
        '<tpl if="finished">',
        '   <div class="section ok">',
        '       <h1>', gettext('Success'), '</h1>',
        '       <p>', interpolate(gettext('%(delivery)s created'), {delivery: gettext('Delivery')}, true), '.',
        '           <tpl if="agroup">',
        //'               <a href="{DEVILRY_URLPATH_PREFIX}/student/assignmentgroup/{agroup.id}?deliveryid={delivery.id}">',
        '               <a href="{DEVILRY_URLPATH_PREFIX}/devilry_student/#/group/{agroup.id}/{delivery.id}">',
        '                   ', interpolate(gettext('View the %(delivery)s', {delivery: gettext('delivery')}, true)), '.</a>',
        '           </tpl>',
        '       </p>',
        '   </div>',
        '</tpl>',
        '<tpl if="!finished">',
        '   <tpl if="filenameCount &gt; 0">',
        '      <div class="section info">',
        '          <h1>', gettext('File uploaded successfully'), '</h1>',
        '          <p>', gettext('Click the Deliver-button to deliver these {filenameCount} files, or choose <em>Add new file</em> to upload more files.'), '</p>',
        '      </div>',
        '   </tpl>',
        '   <tpl if="filenameCount == 0">',
        '      <div class="section help">',
        '          <h1>', interpolate(gettext('Create %(delivery)s'), {delivery: gettext('delivery')}, true), '</h1>',
        '          <p>{initialhelptext}</p>',
        '      </div>',
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
            flex: 5
        });
        this.updateInfoBox();

        this.deliverbutton = Ext.widget('button', {
            text: gettext('Deliver!'),
            scale: 'large',
            disabled: true,
            listeners: {
                scope: this,
                click: this.onDeliver
            }
        });

        Ext.apply(this, {
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [this.infoBoxView, {
                flex: 1,
                xtype: 'fileuploadfield',
                name: 'uploaded_file',
                fieldLabel: gettext('Delivery'),
                hideLabel: true,
                allowBlank: true,
                emptyText: gettext('Select file...'),
                buttonText: gettext('Add new file'),
                margin: '20 0 0 0',
                //height: 70,
                
                listeners: {
                    scope: this,
                    change: this.onAddFile
                }
            }],

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                itemId: 'buttonBar',
                ui: 'footer',
                items: [{
                    xtyle: 'button',
                    scale: 'small',
                    text: gettext('Cancel'),
                    listeners: {
                        scope: this,
                        click: this._onCancel
                    }
                }, '->', this.deliverbutton]
            }]
        });
        this.callParent(arguments);
    },


    /**
     * @private
     */
    updateInfoBox: function(finished) {
        this.infoBoxView.update({
            filenameCount: this.uploadedFilesStore.count(),
            initialhelptext: this.initialhelptext,
            finished: finished,
            delivery: (this.deliveryrecord? this.deliveryrecord.data: null),
            DEVILRY_URLPATH_PREFIX: DevilrySettings.DEVILRY_URLPATH_PREFIX,
            agroup: (this.agroup_recordcontainer.record? this.agroup_recordcontainer.record.data: null)
        });
    },



    /**
     * @private
     */
    createInitialDelivery: function() {
        this.setLoading(interpolate(gettext('Initializing %(delivery)s...'), {
            delivery: gettext('delivery'),
        }, true));
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
        this.setLoading(false);
        this.uploadFileInForm();
    },

    /**
     * @private
     */
    onCreateDeliveryFailure: function(unused, operation) {
        this.setLoading(false);
        //console.log(operation);
        var message = interpolate(gettext('Could not create %(delivery)s on the selected deadline.'), {
            delivery: gettext('delivery')
        }, true);
        var response = Ext.JSON.decode(operation.response.responseText);
        if(response && response.items.errormessages) {
            message = response.items.errormessages.join('. ');
        }
        Ext.MessageBox.show({
            title: gettext('Error'),
            msg: message,
            icon: Ext.MessageBox.ERROR,
            buttons: Ext.MessageBox.OK
        });
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
            this.setLoading(gettext('Uploading your file ...'));
            form.submit({
                url: url,
                scope: this,
                params: {deliveryid: this.deliveryrecord.data.id},
                success: this.onAddFileSuccess,
                failure: this.onAddFileFailure
            });
        }
    },

    /**
     * @private
     */
    onAddFileSuccess: function(form, res) {
        this.setLoading(false);
        this.uploadedFilesStore.add({filename: res.result.file});

        this.uploadedFiles.push(res.result.file);
        this.updateInfoBox();
        this.deliverbutton.enable(); // really only needed on first upload, but it does not hurt.
    },

    /**
     * @private
     */
    onAddFileFailure: function(form, res) {
        this.setLoading(false);
        var errormsg = gettext('Error during upload. Please try again.')
        try {
            var responseData = Ext.JSON.decode(res.response.responseText);
            errormsg = responseData.errormessages[0];
        } catch(e) {}
        Ext.Msg.alert(gettext('Error'), errormsg);
    },



    /**
     * @private
     */
    onDeliver: function() {
        this.deliveryrecord.data.successful = true;
        this.setLoading(gettext('Saving' + '...'));
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
        this.remove(this.down('fileuploadfield'));
        this.removeDocked(this.down('#buttonBar'));
        this.updateInfoBox(true);
        this.deliveryrecord = null;
        this.setLoading(false);
    },

    /**
     * @private
     */
    onDeliverFailure: function() {
        this.setLoading(false);
        Ext.Msg.alert(gettext('Error'), interpolate(gettext('Error when finalizing the %(delivery)s. Please re-try.'), {delivery: gettext('delivery')}, true));
    },


    _onCancel: function() {
        if(this.uploadedFiles.length > 0) {
            var msg = gettext('Are you sure you want to cancel/abort this %(delivery)s? Your uploaded files: %(fileListing)s will be removed from Devilry.');
            Ext.MessageBox.show({
                title: gettext('Confirm cancel'),
                msg: interpolate(msg, {
                    fileListing: '<pre>' + this.uploadedFiles.join("\n") + '</pre>',
                    delivery: gettext('delivery')
                }, true),
                buttons: Ext.MessageBox.OKCANCEL,
                icon: Ext.MessageBox.WARNING,
                scope: this,
                fn: function(buttonname) {
                    if(buttonname == 'ok') {
                        this._cancel();
                    }
                }
            });
        } else {
            this._cancel();
        }
    },

    _cancel: function() {
        window.location.href = DASHBOARD_URL;
    }
});
