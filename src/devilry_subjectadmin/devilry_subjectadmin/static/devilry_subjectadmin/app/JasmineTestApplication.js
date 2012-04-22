Ext.define('devilry_subjectadmin.JasmineTestApplication', {
    extend: 'devilry_subjectadmin.TestApplication',
    requires: ['jsapp.JasmineTest'],

    launch: function() {
        jsapp.JasmineTest.execute();
    }
});
