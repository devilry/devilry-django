/** Panel to show StaticFeedback info .
 *
 * @xtype staticfeedbackeditableinfo
 */
Ext.define('devilry.extjshelpers.StaticFeedbackEditableInfo', {
    extend: 'devilry.extjshelpers.StaticFeedbackInfo',
    alias: 'widget.staticfeedbackeditableinfo',

    constructor: function(config) {
        this.addEvents('clickNewFeedback');
        return this.callParent([config]);
    },

    initComponent: function() {

        var me = this;
        this.createButton = Ext.create('Ext.button.Button', {
            text: 'New feedback',
            margin: {left: 5},
            hidden: true,
            listeners: {
                click: function() {
                    //me.fireEvent('clickNewFeedback');
                    me.loadFeedbackEditor();
                }
            }
        });
        this.addListener('afterStoreLoad', function() {
            if(!me.storeLoadedOnce) {
                this.getHeader().add(me.createButton);
            }
            if(this.assignmentid) {
                this.showViewTools();
            }
        });
        this.callParent(arguments);
    },

    showNewFeedbackButton: function(assignmentid) {
        this.assignmentid = assignmentid;
        this.createButton.show();
    },


    loadFeedbackEditor: function() {
        this.hideViewTools();
        this.removeAll();
        this.add({
            xtype: 'container',
            loader: {
                url: Ext.String.format('/gradeeditors/load-grade-editor/{0}', this.assignmentid),
                renderer: 'component',
                autoLoad: true,
                loadMask: true
            }
        });
    },

    loadFeedbackViewer: function() {
        this.loadStore();
    },

    hideViewTools: function() {
        this.createButton.hide();
        this.feedbackSelector.hide();
    },
    showViewTools: function() {
        this.createButton.show();
        this.feedbackSelector.show();
    },
});
