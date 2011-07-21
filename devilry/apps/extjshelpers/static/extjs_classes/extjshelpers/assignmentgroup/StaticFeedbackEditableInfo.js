/** Panel to show StaticFeedback info and create new static feedbacks.
 *
 * @xtype staticfeedbackeditableinfo
 */
Ext.define('devilry.extjshelpers.assignmentgroup.StaticFeedbackEditableInfo', {
    extend: 'devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditableinfo',

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
            margin: {left: 5},
            listeners: {
                click: function() {
                    me.loadFeedbackEditor();
                }
            }
        });
        this.addListener('afterStoreLoadMoreThanZero', function() {
            me.getToolbar().add(me.createButton);
            me.getToolbar().show();
        });
        this.callParent(arguments);
    },

    loadFeedbackEditor: function() {
        this.getToolbar().hide();
        this.setBody({
            xtype: 'container',
            loader: {
                url: Ext.String.format('/static/gradeeditors/approved.js'),
                renderer: 'component',
                autoLoad: true,
                loadMask: true
            }
        });
    },

    bodyWithNoFeedback: function() {
        var me = this;
        this.setBody({
            xtype: 'component',
            cls: 'no-feedback-editable',
            html: '<p>No feedback</p><p class="unimportant">Click to create feedback</p>',
            listeners: {
                render: function() {
                    this.getEl().addListener('mouseup', me.loadFeedbackEditor, me);
                }
            }
        });
    }
});
