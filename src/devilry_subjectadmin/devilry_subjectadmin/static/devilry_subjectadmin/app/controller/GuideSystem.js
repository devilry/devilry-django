Ext.define('devilry_subjectadmin.controller.GuideSystem', {
    extend: 'Ext.app.Controller',

    views: [
        'guidesystem.GuideView',
        'guidesystem.GuideList'
    ],

    requires: [
        'devilry_subjectadmin.view.guides.CreateNewAssignment',
        'devilry_subjectadmin.view.guidesystem.Pointer'
    ],

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
            },
            'viewport guidesystemlist': {
                guideclick: this._onGuideClick
            }
        });
    },

    _onClose: function() {
        this.getBody().removeAll();
    },

    _onRender: function() {
        //this.showGuide('guide-createnewassignment');
    },

    _onGuideClick: function(list, xtype) {
        console.log('show', xtype);
        this.showGuide(xtype);
    },

    showGuide: function(xtype) {
        this.getGuideView().show();
        this.getBody().removeAll();
        this.getBody().add({
            xtype: xtype,
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
        this._setNotLoading();
        this.getProgress().update({
            current: current,
            total: total
        });
    },

    _isVisible: function() {
        var view = this.getGuideView();
        var isVisible = !Ext.isEmpty(view) && view.isVisible();
        return isVisible;
    },

    setLoading: function() {
        if(this._isVisible()) {
            this.getGuideView().setLoading();
        }
    },
    _setNotLoading: function() {
        if(this._isVisible()) {
            this.getGuideView().setLoading(false);
        }
    },

    pointAt: function(element) {
        this.pointer.pointAt(element);
    }
});
