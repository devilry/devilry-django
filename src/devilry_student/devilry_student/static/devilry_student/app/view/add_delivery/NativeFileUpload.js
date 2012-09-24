Ext.define('devilry_student.view.add_delivery.NativeFileUpload', {
    extend: 'Ext.Component',
    alias: 'widget.native_file_upload',
    cls: 'bootstrap',
    margin: '40 0 40 0',

    mixins: [
        'Ext.form.field.Field'
    ],
    renderTpl: [
        '<input id="{id}-fileInputEl" type="file" class="native-fileupload-filefield" ',
            // NOTE: We put the onchange event handler here instead of in a delegate to make IE8 work
            'onchange="Ext.getCmp(\'{id}\').onFileChange(this)"/>'
    ],
    childEls: ['fileInputEl'],

    initComponent: function() {
        this.callParent(arguments);
        this.on('render', this._onRender, this);
    },

    setValue: function(value) {
        if(Ext.isEmpty(value)) {
            this.reset();
        } else {
            throw "It is not possible to set the value of a file field in all browsers, so we do not support any other value than an empty string.";
        }
    },

    _onRender: function() {
        this.fileInputEl.dom.name = this.getName();
    },

    isFileUpload: function() {
        return true;
    },

    onFileChange: function(domelement) {
        var element = Ext.dom.Element(domelement);
        this.lastValue = null; // force change event to get fired even if the user selects a file with the same name                
        this.value = element.value;
        this.checkChange();
    },

    extractFileInput: function() {
        if(this.isFileUpload()) {
            var fileInput = this.fileInputEl.dom;
            var clone = fileInput.cloneNode(true);
            fileInput.parentNode.replaceChild(clone, fileInput);
            this.inputEl = Ext.get(clone);
            return fileInput;
        } else {
            return null;
        }
    },

    onDestroy: function(){
        Ext.destroyMembers(this, 'fileInputEl');
        this.callParent();
    },

    _getPositionInContainer: function() {
        var container = this.up();
        var index = container.items.findIndexBy(function(item) {
            return item == this;
        }, this);
        if(index === -1) {
            throw "Position in container not found";
        } else {
            return index;
        }
    },

    reset: function() {
        var index = this._getPositionInContainer();
        var container = this.up();
        var itemId = this.itemId;
        var name = this.name;
        container.remove(this);
        container.add({
            xtype: 'native_file_upload',
            itemId: itemId,
            name: name
        });
    },

    _onFileChange: function(e) {
        var element = Ext.dom.Element(e.target);
        this.lastValue = null; // force change event to get fired even if the user selects a file with the same name                
        this.value = element.value;
        this.checkChange();
    }
});
