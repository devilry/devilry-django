Ext.define('subjectadmin.JasmineTestApplication', {
    extend: 'subjectadmin.TestApplication',

    launch: function() {
        jasmine.getEnv().addReporter(new jasmine.TrivialReporter());
        jasmine.getEnv().execute();
    }
});
