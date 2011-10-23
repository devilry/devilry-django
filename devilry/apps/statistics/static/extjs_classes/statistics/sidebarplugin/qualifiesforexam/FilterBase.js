Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase', {
    extend: 'Ext.container.Container',

    config: {
        loader: undefined,
        aggregatedStore: undefined,
        labelname: undefined,
        title: undefined
    },

    constructor: function(config) {
        this.saveButton = Ext.widget('button', {
            text: 'Save',
            iconCls: 'icon-save-32',
            scale: 'large',
            flex: 1,
            listeners: {
                scope: this,
                click: this._onSave
            }
        });
        this.previewButton = Ext.widget('button', {
            text: 'Show matching students',
            //iconCls: '',
            scale: 'large',
            flex: 1,
            listeners: {
                scope: this,
                click: this._onPreview
            }
        });

        this.defaultButtonPanel = Ext.widget('container', {
            items: [this.previewButton, this.saveButton],
            layout: {
                type: 'hbox',
                align: 'top'
            },
            height: 60
        });
        this.callParent([config]);
        this.initConfig(config);
    },

    _onSave: function() {
        if(!this.validInput()) {
            return;
        }
        Ext.MessageBox.show({
            title: 'Save?',
            msg: 'Are you sure you want to save? Students will be able to see if they are qualified for final exams.',
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            closable: false,
            scope: this,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this.loader.labelManager.setLabels({
                        filter: this.filter,
                        scope: this,
                        label: this.labelname,
                        student_can_read: true
                    });
                }
            }
        });
    },

    _onPreview: function() {
        if(this.validInput()) {
            this.loader.clearFilter();
            this.loader.filterBy(this.title, this.filter, this);
        }
    },

    validInput: function() {
        return true;
    }
});
