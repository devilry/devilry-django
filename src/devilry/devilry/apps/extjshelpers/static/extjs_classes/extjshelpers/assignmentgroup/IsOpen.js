Ext.define('devilry.extjshelpers.assignmentgroup.IsOpen', {
    extend: 'Ext.container.Container',
    alias: 'widget.assignmentgroup_isopen',
    cls: 'widget-assignmentgroup_isopen',
    config: {
        assignmentgroup_recordcontainer: undefined,
        canExamine: undefined
    },

    tooltips: {
        canExamine: gettext('Click to toggle open/closed. A group should remain open until you have finished grading them. Devilry normally opens and closes groups for you automatically. You may want to manually close a group if you want to make the current grade their final grade on this assignment. A closed group can be re-opened at any time.'),
        student: 'As long as the assignment is open for more deliveries, you can add as many deliveries as you like, and your examiner(s) will normally correct your latest delivery. When an assignment is closed, the latest feedback is your final grade on this assignment. If you have not been given feedback, and you think this is wrong, you should contact your examiner or course administrator.'
    },
    layout: 'fit',
    //style: 'border: none',

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        if(this.assignmentgroup_recordcontainer.record) {
            this.onSetRecord();
        } else {
            this.assignmentgroup_recordcontainer.on('setRecord', this.onSetRecord, this);
        }
        this.callParent(arguments);
    },

    /**
     * @private
     */
    onSetRecord: function() {
        this.removeAll();
        var buttonText;
        if(this.assignmentgroup_recordcontainer.record.get('is_open')) {
            buttonText = '<i class="icon-folder-open"></i> ' + gettext('Open - click to close');
        } else {
            buttonText = '<i class="icon-folder-close"></i> ' + gettext('Closed - click to open');
        }
        if(this.canExamine) {
            this.add({
                xtype: 'button',
                scale: 'medium',
                cls: 'bootstrap',
                text: buttonText,
//                ui: 'inverse',
                listeners: {
                    scope: this,
                    click: this.onStatusButtonClick,
                    render: function(button) {
                        Ext.tip.QuickTipManager.register({
                            target: button.getEl(),
                            title: gettext('How open/closed works'),
                            text: this.tooltips.canExamine,
                            width: 350,
                            dismissDelay: 30000 // Hide after 30 seconds hover
                        });
                    }
                }
            });
        } else {
            this.add({
                xtype: 'box',
                cls: 'text_with_tooltip',
                html: this.assignmentgroup_recordcontainer.record.data.is_open? 'Open - more deliveries allowed': 'Closed - final grade given',
                listeners: {
                    scope: this,
                    render: function(button) {
                        Ext.tip.QuickTipManager.register({
                            target: button.getEl(),
                            title: 'How open/closed works',
                            text: this.tooltips.student,
                            width: 300,
                            dismissDelay: 30000 // Hide after 30 seconds hover
                        });
                    }
                }
            });
        }
    },


    /**
     * @private
     */
    onStatusButtonClick: function() {
        //console.log(this.id);
        if(this.assignmentgroup_recordcontainer.record.data.is_open) {
            this.onCloseGroup();
        } else {
            this.onOpenGroup();
        }
    },


    /**
     * @private
     */
    onOpenGroup: function() {
        var win = Ext.MessageBox.show({
            title: 'Are you sure you want to open this group?',
            msg: '<p>This will <strong>allow</strong> students to add more deliveries. ' +
                'Normally Devilry will close groups automatically when:</p>'+
                '<ul>' +
                '   <li>you have given a passing grade.</li>' +
                '   <li>students have failed to get a passing grade more than the configured maximum number of times.</li>' +
                '</ul>' +
                '<p>And you normally do not open it again unless you want students to add a new delivery.</p>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId === 'yes') {
                    this.assignmentgroup_recordcontainer.record.data.is_open = true;
                    this.assignmentgroup_recordcontainer.record.save({
                        scope: this,
                        success: function(record) {
//                            this.assignmentgroup_recordcontainer.fireSetRecordEvent();
                            window.location.reload();
                        },
                        failure: function() {
                            throw "Failed to open group.";
                        }
                    });
                }
            }
        });
    },

    /**
     * @private
     */
    onCloseGroup: function() {
        var statics = this.statics();
        var win = Ext.MessageBox.show({
            title: 'Are you sure you want to close this group?',
            msg: '<p>This will <strong>prevent</strong> students from adding more deliveries. ' +
                'Normally Devilry will close groups automatically when:</p>'+
                '<ul>' +
                '   <li>you have given a passing grade.</li>' +
                '   <li>students have failed to get a passing grade more than the configured maximum number of times.</li>' +
                '</ul>' +
                '<p>However you may have to close a group manually if no maximum number of tries have been configured, or if you want the current feedback to be stored as the final feedback for this group.</p>',
            buttons: Ext.Msg.YESNO,
            scope: this,
            closable: false,
            fn: function(buttonId) {
                if(buttonId === 'yes') {
                    statics.closeGroup(this.assignmentgroup_recordcontainer, function() {
                        window.location.reload();
                    });
                }
            }
        });
    },

    statics: {
        closeGroup: function(assignmentgroup_recordcontainer, callbackFn, callbackScope) {
            assignmentgroup_recordcontainer.record.data.is_open = false;
            assignmentgroup_recordcontainer.record.save({
                success: function(record) {
                    assignmentgroup_recordcontainer.fireSetRecordEvent();
                    Ext.callback(callbackFn, callbackScope);
                },
                failure: function() {
                    throw "Failed to close group.";
                }
            });
        }
    }
});
