Ext.define('devilry.administrator.studentsmanager.AddDeliveriesMixin', {
    //requires: [
        //'devilry.student.FileUploadPanel'
        //'devilry.administrator.studentsmanager.LocateGroup'
    //],

    deliveryTypes: {
        TYPE_ELECTRONIC: 0,
        TYPE_NON_ELECTRONIC: 1,
        TYPE_ALIAS: 2
    },

    //onPreviouslyApproved: function() {
        //this.down('studentsmanager_studentsgrid').selModel.select(1);
        //if(this.noneSelected()) {
            //this.onNotSingleSelected();
            //return;
        //}
        //var groupRecord = this.getSelection()[0];
        //console.log(groupRecord);

        ////this.assignmentgroupPrevApprovedStore.proxy.extraParams.filters = Ext.JSON.encode([{
            ////field: 'parentnode__parentnode__parentnode',
            ////comp: 'exact',

        //Ext.widget('window', {
            //width: 800,
            //height: 700,
            //modal: true,
            //maximizable: true,
            //layout: 'fit',
            //title: 'Select previously approved group',
            //items: {
                //xtype: 'locategroup',
                //store: this.assignmentgroupPrevApprovedStore,
                //groupRecord: groupRecord
            //}
        //}).show();

        ////this.refreshStore();
    //},

    onAddNonElectronicDelivery: function() {
        if(!this.singleSelected()) {
            this.onNotSingleSelected();
            return;
        }
        var groupRecord = this.getSelection()[0];
        
        var msg = Ext.create('Ext.XTemplate',
            '<p>Are you sure you want to create a dummy delivery for <em>',
            '    <tpl if="name">',
            '        {name}: ',
            '    </tpl>',
            '    <tpl for="candidates__identifier">',
            '        {.}<tpl if="xindex &lt; xcount">, </tpl>',
            '    </tpl>',
            '</em>?',
            '<tpl if="number_of_deliveries &gt; 0">',
            '   <p><strong>WARNING:</strong> One usually only creates dummy deliveries for groups with no ',
            '   deliveries, however this group has <strong>{number_of_deliveries}</strong> deliveries.</p>',
            '</tpl>'
        );
        var me = this;
        Ext.MessageBox.show({
            title: 'Confirm that you want to create dummy delivery',
            msg: msg.apply(groupRecord.data),
            animateTarget: this.deletebutton,
            buttons: Ext.Msg.YESNO,
            icon: (groupRecord.data.number_of_deliveries>0? Ext.Msg.WARNING: Ext.Msg.QUESTION),
            fn: function(btn) {
                if(btn == 'yes') {
                    me.addNonElectronicDelivery(groupRecord);
                }
            }
        });
    },

    /**
     * @private
     */
    addNonElectronicDelivery: function(groupRecord) {
        var delivery = this.createDeliveryRecord(groupRecord, this.deliveryTypes.TYPE_NON_ELECTRONIC);
        delivery.save();
        this.refreshStore();
    },


    onPreviouslyPassed: function() {
        //this.down('studentsmanager_studentsgrid').selModel.select(1);
        if(this.noneSelected()) {
            this.onSelectNone();
            return;
        }
        this.prevPassedIntro();
    },

    /**
     * @private
     */
    prevPassedIntro: function() {
        Ext.widget('window', {
            width: 500,
            height: 400,
            layout: 'fit',
            modal: true,
            title: 'Mark as delivered in a previous period',
            items: {
                'xtype': 'panel',
                frame: false,
                border: false,
                html:
                    '<div class="section helpsection">' +
                    '   <p>Marking a group as delivered in a previoud period/semester, does the following:</p>' +
                    '   <ul>' +
                    '       <li>Create a new <em>empty</em> delivery that is marked as imported from a previous semester. This is done automatically.</li>' +
                    '       <li>Create a feedback for the new <em>fake</em> delivery using the grade editor configured for this assignment.</li>' +
                    '   </ul>' +
                    '   <p>Click <em>next</em> to create the feedback. The feedback you select will be applied to each selected group.</p>' +
                    '</section>'
            },

            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    iconCls: 'icon-next-32',
                    scale: 'large',
                    text: 'Next',
                    listeners: {
                        scope: this,
                        click: function(button) {
                            button.up('window').close();
                            this.prevPassedGiveFeedbackToSelected();
                        }
                    }
                }]
            }]
        }).show();
    },

    /**
     * @private
     */
    prevPassedGiveFeedbackToSelected: function() {
        var draftEditor = Ext.create('devilry.gradeeditors.EditManyDraftEditorWindow', {
            isAdministrator: this.isAdministrator,
            gradeeditor_config: this.gradeeditor_config_recordcontainer.record.data,
            registryitem: this.registryitem_recordcontainer.record.data,
            buttonText: 'Next',
            buttonIcon: 'icon-next-32',
            listeners: {
                scope: this,
                createNewDraft: this.prevPassedOnPublishFeedback
            }
        });
        draftEditor.show();
    },


    /**
     * @private
     */
    prevPassedOnPublishFeedback: function(feedbackdraftModelName, draftstring) {
        //this.down('studentsmanager_studentsgrid').selModel.selectAll();
        this.progressWindow.start('Mark as delivered in a previous period');
        this._finishedSavingGroupCount = 0;
        //this.down('studentsmanager_studentsgrid').performActionOnSelected({
            //scope: this,
            //callback: this.createPreviouslyPassedDelivery,
            //extraArgs: [feedbackdraftModelName, draftstring]
        //});

        this.down('studentsmanager_studentsgrid').gatherSelectedRecordsInArray({
            scope: this,
            callback: function(groupRecords) {
                if(this.anyGroupHaveDeliveries(groupRecords)) {
                    Ext.MessageBox.show({
                        title: 'Selected groups that have deliveries',
                        msg: '<p>One or more of the selected groups have deliveries.</p><p>This usually means that they have made a delivery that should be corrected instead of marking the assignment as corrected in a previous period.</p><p>Click <em>yes</em> to continue, or click <em>no</em> to cancel this operation.</p>',
                        buttons: Ext.Msg.YESNO,
                        icon: Ext.Msg.WARNING,
                        scope: this,
                        fn: function(btn) {
                            if(btn == 'yes') {
                                this.createPreviouslyPassedDeliveries(groupRecords, feedbackdraftModelName, draftstring);
                            }
                        }
                    });
                } else {
                    this.createPreviouslyPassedDeliveries(groupRecords, feedbackdraftModelName, draftstring);
                }
            },
        });
    },

    /**
     * @private
     */
    createPreviouslyPassedDeliveries: function(groupRecords, feedbackdraftModelName, draftstring) {
        Ext.each(groupRecords, function(groupRecord, index) {
            this.createPreviouslyPassedDelivery(groupRecord, index, groupRecords.length, feedbackdraftModelName, draftstring);
        }, this);
    },

    /**
     * @private
     */
    anyGroupHaveDeliveries: function(groupRecords) {
        for(i=0; i<groupRecords.length; i++) {
            var groupRecord = groupRecords[i];
            if(groupRecord.data.number_of_deliveries > 0) {
                return true;
            }
        }
        return false;
    },

    /**
     * @private
     */
    createPreviouslyPassedDelivery: function(groupRecord, index, total, feedbackdraftModelName, draftstring) {
        var msg = Ext.String.format('Creating a delivery on group {0}/{1}', index, total);
        this.getEl().mask(msg);

        var delivery = this.createDeliveryRecord(groupRecord, this.deliveryTypes.TYPE_ALIAS);
        delivery.save({
            scope: this,
            failure: function() {
                this.progressWindow.addErrorFromOperation(
                    groupRecord, 'Failed to create delivery', operation
                );
            },
            success: function(record) {
                groupRecord.data.latest_delivery_id = record.data.id;
                this.giveFeedbackToSelected(groupRecord, index, total, feedbackdraftModelName, draftstring);
            }
        });
    },


    createDeliveryRecord: function(groupRecord, deliveryType) {
        var modelname = Ext.String.format('devilry.apps.{0}.simplified.SimplifiedDelivery', this.role);
        return Ext.create(modelname, {
            successful: true,
            deadline: groupRecord.data.latest_deadline_id,
            delivery_type: deliveryType
            //alias_delivery
        });
    }
});
