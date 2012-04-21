Ext.define('themebase.JasmineTestApplication', {
    extend: 'Ext.app.Application',
    requires: ['jsapp.JasmineTest'],

    launch: function() {
        jsapp.JasmineTest.execute();
    }
});
