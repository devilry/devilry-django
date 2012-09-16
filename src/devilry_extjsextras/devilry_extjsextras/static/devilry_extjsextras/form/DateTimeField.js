/**
 * Based on http://www.sencha.com/forum/showthread.php?134345-Ext.ux.form.field.DateTime
 */
Ext.define('devilry_extjsextras.form.DateTimeField', {
    extend: 'Ext.form.FieldContainer',
    mixins:{    
        field:'Ext.form.field.Field'
    },
    alias: 'widget.devilry_extjsextras-datetimefield',
        
    //configurables
    
    combineErrors: true,
    msgTarget: 'under',    
    readOnly: false,

    /**
     * @cfg {Object} dateConfig
     * Additional config options for the date field.
     */
    dateConfig:{},

    /**
     * @cfg {Object} timeConfig
     * Additional config options for the time field.
     */
    timeConfig:{},

    /**
     * @cfg {string} dateFieldEmptyText ``emptyText`` attribute for the date field.
     */
    dateFieldEmptyText: pgettext('extjs date emptytext', 'YYYY-MM-DD'),

    /**
     * @cfg {string} dateFieldEmptyText ``emptyText`` attribute for the time field.
     */
    timeFieldEmptyText: pgettext('extjs time emptytext', 'hh:mm'),
    

    initComponent: function(){
        this.childrenRendered = 0;
        this.currentValue = null;
        Ext.apply(this, {
            layout: 'column',
            items: [Ext.Object.merge({
                xtype: 'devilry_extjsextras_datefield',
                columnWidth: 0.5,
                isFormField: false, //exclude from field query's
                emptyText: this.dateFieldEmptyText,
                submitValue:false,
                listeners: {
                    scope: this,
                    render: this._onChildRender,
                    blur: this._onItemBlur,
                    change: this._onFieldChange,
                    focus: this._onItemFocus
                }
            }, this.dateConfig), Ext.Object.merge({
                xtype: 'devilry_extjsextras_timefield',
                columnWidth: 0.5,
                isFormField:false, //exclude from field query's
                emptyText: this.timeFieldEmptyText,
                submitValue:false,
                listeners: {
                    scope: this,
                    render: this._onChildRender,
                    blur: this._onItemBlur,
                    change: this._onFieldChange,
                    focus: this._onItemFocus
                }
            }, this.timeConfig)]
        });

        
        //for (var i=0; i < this.items.length; i++) {
            //this.items[i].on('specialkey', function(field, event){
                //var key = event.getKey();
                //var tab = key == event.TAB;
                
                //if (tab && this.focussedItem == this.getDateField()) {
                    //event.stopEvent();
                    //this.getTimeField().focus();
                    //return;
                //}
                
                //this.fireEvent('specialkey', field, event);
            //});
        //}

        this.callParent(arguments);
        
        // this dummy is necessary because Ext.Editor will not check whether an inputEl is present or not
        this.inputEl = {
            dom:{},
            swallowEvent:function(){}
        };

        this.initField();
    },

    getDateField: function() {
        return this.down('devilry_extjsextras_datefield');
    },
    getTimeField: function() {
        return this.down('devilry_extjsextras_timefield');
    },

    _onFieldChange: function(timefield, newValue, oldValue) {
        var oldFullValue = this.currentValue;
        var newFullValue = this.getValue();
        if(this.newFullValue !== null) {
            this.currentValue = newFullValue;
            this.fireEvent('change', this, newFullValue, oldFullValue);
        }
    },

    _onChildRender: function() {
        this.childrenRendered ++;
        if(this.childrenRendered == 2) {
            this.fireEvent('allRendered', this);
        }
    },
    
    focus:function(){
        this.callParent();
        this.getDateField().focus();
    },

    _onItemFocus: function(item){
        if (this.blurTask){
            this.blurTask.cancel();
        }
        this.focussedItem = item;
    },
    
    _onItemBlur: function(item){
        if (item != this.focussedItem) {
            return;
        }
        // 100ms to focus a new item that belongs to us, otherwise we will assume the user left the field
        this.blurTask = new Ext.util.DelayedTask(function(){
            this.fireEvent('blur', this);
        }, this);
        this.blurTask.delay(100);
    },
    
    getValue: function(){
        var value = null;
        var date = this.getDateField().getSubmitValue()
        if (date){
            var time = this.getTimeField().getSubmitValue()
            if (time){
                var format = this.getFormat();
                value = Ext.Date.parse(date + ' ' + time, format);
            } else {   
                value = this.getDateField().getValue();
            }
        }
        return value;
    },
    
    getSubmitValue: function(){   
        var format = this.getFormat()
        var value = this.getValue();
        return value ? Ext.Date.format(value, format) : null;        
    },
 
    setValue: function(value){    
        if (Ext.isString(value)){
            value = Ext.Date.parse(value, this.getFormat());
        }
        this.getDateField().setValue(value);
        this.getTimeField().setValue(value);
    },
    
    getFormat: function(){
        return (this.getDateField().submitFormat || this.getDateField().format) + " " + (this.getTimeField().submitFormat || this.getTimeField().format);
    },
    
    // Bug? A field-mixin submits the data from getValue, not getSubmitValue
    getSubmitData: function(){
        var data = null;
        if (!this.disabled && this.submitValue && !this.isFileUpload()) {
            data = {};
            data[this.getName()] = '' + this.getSubmitValue();
        }
        return data;
    },

    isValid: function() {
        return this.getDateField().isValid() && this.getTimeField().isValid();
    }
});
