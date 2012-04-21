Ext.define('subjectadmin.JasmineTestApplication', {
    extend: 'subjectadmin.TestApplication',
    requires: ['jsapp.JasmineTest'],

    launch: function() {
        jsapp.JasmineTest.execute();
    }
});
