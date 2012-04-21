/** Static class that provides a single method, ``execute``, that should be
 * used to execute jasmine tests. */
Ext.define('jsapp.JasmineTest', {
    statics: {
        /** Execute jasmine tests. */
        execute: function() {
            jasmine.getEnv().addReporter(new jasmine.TrivialReporter());
            jasmine.getEnv().execute();
        }
    }
});
