Ext.define('devilry_subjectadmin.controller.guides.Base', {
    extend: 'Ext.app.Controller',

    /**
     * @property {int} [steps]
     * Number of steps. Used by ``setStep()``.
     */

    /**
     * @property {String} [title]
     * The title of the guide.
     */


    init: function() {
        this.application.addListener({
            scope: this,
            beforeroute: this._onBeforeRoute
        });
        this.control({
            'viewport guide-createnewassignment': {
                render: this.onRender
            }
        });
    },

    _onBeforeRoute: function() {
        if(!Ext.isEmpty(this.guideSystem)) {
            this.guideSystem.setLoading();
        }
    },

    onRender: function() {
        this.guideSystem = this.getGuideView().guideSystem
        this.guideSystem.setTitle(this.title);
        Ext.defer(function() {
            this.onFirstStep();
        }, 100, this);
    },

    onFirstStep: function() {
        throw "onFirstStep must be implemented in subclasses";
    },

    isActive: function() {
        var view = this.getGuideView();
        var isActive = !Ext.isEmpty(view) && view.isVisible();
        return isActive;
    },

    setStep: function(cardItemId, progress) {
        this.getGuideView().getLayout().setActiveItem(cardItemId);
        this.guideSystem.setProgress(progress, this.steps);
    }
});
