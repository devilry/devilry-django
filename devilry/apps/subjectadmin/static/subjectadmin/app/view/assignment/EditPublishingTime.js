/**
 * A window for editing the publishing time of an Assignment.
 * */
Ext.define('subjectadmin.view.assignment.EditPublishingTime', {
    extend: 'Ext.window.Window',
    alias: 'widget.editpublishingtime',
    requires: [
        'themebase.SaveButton'
    ],

    /**
     * @cfg {subjectadmin.model.Assignment} assignmentRecord (required)
     */

    initComponent: function() {
        Ext.apply(this, {
            layout: 'fit',
            width: 330,
            height: 270,
            modal: true,
            title: dtranslate('subjectadmin.assignment.editpublishing.title'),
            items: {
                xtype: 'form',
                bodyPadding: 20,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
                    xtype: 'box',
                    html: dtranslate('subjectadmin.assignment.editpublishing.help'),
                    margin: {bottom: 20}
                }, {
                    xtype: 'alertmessagelist'
                }, {
                    xtype: 'themebase-datetimefield',
                    name: 'publishing_time',
                    margin: {top: 20},
                    value: this.assignmentRecord.get('publishing_time')
                }],
                dockedItems: [{
                    xtype: 'toolbar',
                    dock: 'bottom',
                    ui: 'footer',
                    padding: 0,
                    items: ['->', {
                        xtype: 'savebutton',
                        formBind: true, //only enabled once the form is valid
                        listeners: {
                            scope: this,
                            click: this._onSave
                        }
                    }]
                }]
            }
        });
        this.callParent(arguments);
    },

    _onSave: function() {
        var form = this.down('form').getForm();
        if(form.isDirty()) {
            form.updateRecord(this.assignmentRecord);
            console.log(this.assignmentRecord.get('publishing_time').toString());
            this.getEl().mask(dtranslate('themebase.saving'));
            this.assignmentRecord.save({
                scope: this,
                success: this._onSaveSuccess,
                failure: this._onSaveFailure
            });
        } else {
            this.close();
        }
    },

    _onSaveSuccess: function() {
        this.getEl().unmask();
        this.close();
    },

    _onSaveFailure: function(record, operation) {
        this.getEl().unmask();
        themebase.form.ErrorUtils.handleRestErrorsInForm(
            operation, this.down('form'), this.down('alertmessagelist')
        );
    }
});
