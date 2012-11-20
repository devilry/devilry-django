Ext.define('devilry.statistics.sidebarplugin.qualifiesforexam.FilterBase', {
    extend: 'Ext.container.Container',

    config: {
        loader: undefined,
        path: undefined,
        aggregatedStore: undefined,
        labelname: undefined,
        negative_labelname: undefined,
        title: undefined,
        main: undefined
    },

    constructor: function(config) {
        this.saveButton = Ext.widget('button', {
            text: 'Save',
            iconCls: 'icon-save-32',
            scale: 'large',
            flex: 1,
            tooltip: {
                title: 'Save',
                text: Ext.String.format('Adds labels to students according to your current settings, and marks this period (semester) as ready for export to {0}.', DevilrySettings.DEVILRY_SYNCSYSTEM)
            },
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
            tooltip: {
                title: 'Show matching students',
                text: 'Adds a filter to the table that limits visible rows to the ones matching this rule.'
            },
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
            height: 40
        });
        this.initConfig(config); // Must come before _loadSettings
        this._loadSettings(); // Must come before callParent, because callParent calls initComponent (which needs settings)
        this.callParent([config]);
    },

    _loadSettings: function() {
        if(this.main.settings && this.main.settings.path === this.path) {
            this.settings = this.main.settings.settings;
        }
    },

    _onSave: function() {
        if(!this.validInput()) {
            return;
        }
        Ext.MessageBox.show({
            title: 'Save?',
            msg: Ext.String.format('Are you sure you want to save? Students will be able to see if they are qualified for final exams. It will also mark <em>qualifies for exam</em> as <strong>ready for export</strong> to {0}.', DevilrySettings.DEVILRY_SYNCSYSTEM),
            buttons: Ext.Msg.YESNO,
            icon: Ext.Msg.QUESTION,
            closable: false,
            scope: this,
            fn: function(buttonId) {
                if(buttonId == 'yes') {
                    this._onSaveYes();
                }
            }
        });
    },

    _onSaveYes: function() {
        this.loader.requireCompleteDataset(function() {
            this.main.saveSettings(this.path, this.getSettings(), function() {
                this._saveLabels();
            }, this);
        }, this);
    },

    _saveLabels: function() {
        this.loader.labelManager.setLabels({
            filter: this.filter,
            scope: this,
            label: this.labelname,
            negative_label: this.negative_labelname,
            student_can_read: true
        });
    },

    _onPreview: function() {
        if(this.validInput()) {
            this.loader.requireCompleteDataset(function() {
                this.loader.clearFilter();
                this.loader.filterBy(this.title, this.filter, this);
            }, this);
        }
    },

    validInput: function() {
        return true;
    },

    getSettings: function() {
        return false;
    }
});
