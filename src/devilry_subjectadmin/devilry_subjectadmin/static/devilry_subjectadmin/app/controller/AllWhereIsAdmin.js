Ext.define('devilry_subjectadmin.controller.AllWhereIsAdmin', {
    extend: 'Ext.app.Controller',

    requires: [
    ],

    // Views - the init function of this controller is called when the first of its views is added to the page (which we do in ../app.js)
    views: [
        'allwhereisadmin.AllWhereIsAdminPanel'
    ],

    // Models - Available as get<modelname>()
    models: [
        //'AllWhereIsAdmin',
    ],

    refs: [{
        // Create selector method for the ``allwhereisadminpanel`` widget called getAllWhereIsAdminPanel()
        ref: 'allWhereIsAdminPanel',
        selector: 'allwhereisadminpanel'
    }, {
        ref: 'listOfSubjects',
        selector: 'allwhereisadminpanel #listOfSubjects' // Note: we use the itemId for the selector
    }],

    init: function() {
        this.control({
            // Listen for events by selector
            'viewport allwhereisadminpanel #listOfSubjects': {
                // NOTE: Important that we listen for #listOfSubjects, and not
                // for the panel, since the panel is rendered before the list,
                // which would mess up our code that requires the list to be
                // rendered.
                render: this._onRenderListOfSubjects
            }
        });
    },

    _onRenderListOfSubjects: function() {
        console.log('Rendered');
        // TODO: load the model and move the code below into the load-success handler
        this.getListOfSubjects().update({
            // Refresh the template with new data
            loadingtext: null
        });
    }
});
