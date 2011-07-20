/** Panel to show StaticFeedback info .
 *
 * @xtype staticfeedbackeditableinfo
 */
Ext.define('devilry.extjshelpers.StaticFeedbackEditableInfo', {
    extend: 'devilry.extjshelpers.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditableinfo',

    config: {
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
        this.addListener('afterStoreLoad', function() {
            me.down('toolbar').add(me.createButton);
        });
        this.callParent(arguments);
    },

    loadFeedbackEditor: function() {
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
                    this.getEl().addListener('click', me.loadFeedbackEditor, me);
                }
            }
        });
    }
});
