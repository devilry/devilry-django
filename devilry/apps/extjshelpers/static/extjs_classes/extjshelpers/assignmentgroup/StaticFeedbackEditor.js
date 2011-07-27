/** Panel to show StaticFeedback info and create new static feedbacks.
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditor', {
    extend: 'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditor',
    depends: [
        'devilry.extjshelpers.GradeEditorWindow'
    ],

    config: {
        /**
        * @cfg
        * Assignment id. (Required).
        */
        assignmentid: undefined
    },

    constructor: function(config) {
        return this.callParent([config]);
    },

    initComponent: function() {
        var me = this;
        this.createButton = Ext.create('Ext.button.Button', {
            text: 'New feedback',
            iconCls: 'icon-add-16',
            margin: {left: 5},
            listeners: {
                scope: this,
                click: this.loadGradeEditor
            }
        });
        this.addListener('afterStoreLoadMoreThanZero', function() {
            me.getToolbar().add(me.createButton);
        });
        this.callParent(arguments);
    },

    loadGradeEditor: function() {
        //this.getToolbar().hide();
        Ext.create('devilry.extjshelpers.GradeEditorWindow', {
            deliveryid: this.delivery_recordcontainer.record.data.id,
            items: {
                xtype: 'container',
                loader: {
                    url: Ext.String.format('/static/asminimalaspossible_gradeeditor/drafteditor.js'), // TODO read from an API
                    renderer: 'component',
                    autoLoad: true,
                    loadMask: true
                }
            }
        }).show();
    },

    bodyWithNoFeedback: function() {
        var me = this;
        this.setBody({
            xtype: 'component',
            cls: 'no-feedback-editable',
            html: '<p>No feedback</p><p class="unimportant">Click to create feedback</p>',
            listeners: {
                render: function() {
                    this.getEl().addListener('mouseup', me.loadGradeEditor, me);
                }
            }
        });
    },

    showFeedbackViewer: function() {
        this.onLoadDelivery();
    }
});
