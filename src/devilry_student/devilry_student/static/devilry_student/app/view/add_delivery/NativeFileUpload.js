Ext.define('devilry_student.view.add_delivery.NativeFileUpload', {
    extend: 'Ext.Component',
    alias: 'widget.native_file_upload',
    cls: 'bootstrap',
    margin: '40 0 40 0',

    mixins: [
        'Ext.form.field.Field'
    ],
    renderTpl: [
        '<input id="{id}-fileInputEl" type="file" class="native-fileupload-filefield"/>',
    ],
    childEls: ['fileInputEl'],

    initComponent: function() {
        this.addListener({
            element: 'el',
            delegate: '.native-fileupload-filefield',
            scope: this,
            change: this._onFileChange
        });

        this.callParent(arguments);
        this.on('render', this._onRender, this);
    },

    setValue: function(value) {
        if(Ext.isEmpty(value)) {
            this.reset();
        }
    },

    _onRender: function() {
        this.fileInputEl.dom.name = this.getName();
    },

    isFileUpload: function() {
        return true;
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

    reset: function(){
        this.fileInputEl.dom.value = '';
    },

    _onFileChange: function(e) {
        var element = Ext.dom.Element(e.target);
        this.lastValue = null; // force change event to get fired even if the user selects a file with the same name                
        this.value = element.value;
        this.checkChange();
    }
});
