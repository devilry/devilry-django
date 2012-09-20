Ext.define('devilry_subjectadmin.controller.GuideSystem', {
    extend: 'Ext.app.Controller',

    views: [
        'guidesystem.GuideView'
    ],

    requires: [
        'devilry_subjectadmin.view.guides.CreateNewAssignment',
        'devilry_subjectadmin.view.guidesystem.Pointer'
    ],

    guides: {
        'guide-createnewassignment': {
        }
    },

    refs: [{
        ref: 'guideView',
        selector: 'viewport guidesystemview'
    }, {
        ref: 'progress',
        selector: 'viewport guidesystemview #progress'
    }, {
        ref: 'body',
        selector: 'viewport guidesystemview #body'
    }],

    init: function() {
        this.pointer = Ext.widget('guidesystem_pointer', {
            hidden: true,
        });
        this.application.addListener({
            scope: this,
            beforeroute: this._onBeforeRoute
        });
        this.control({
            'viewport guidesystemview': {
                render: this._onRender,
                close: this._onClose
            }
        });
    },

    _onClose: function() {
        this.getBody().removeAll();
    },

    _onRender: function() {
        this.getBody().add({
            xtype: 'guide-createnewassignment',
            guideSystem: this
        });
    },

    _onBeforeRoute: function() {
        this.pointer.stopPointAt();
    },

    setTitle: function(title) {
        this.getGuideView().setTitle(title);
    },

    setProgress: function(current, total) {
        this.getProgress().update({
            current: current,
            total: total
        });
    },

    pointAt: function(element) {
        this.pointer.pointAt(element);
    }
});
