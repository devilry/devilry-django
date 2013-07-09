Ext.define('devilry_subjectadmin.controller.GuideSystem', {
    extend: 'Ext.app.Controller',

    views: [
        'guidesystem.GuideView',
        'guidesystem.GuideList'
    ],

    requires: [
        'devilry_subjectadmin.view.guides.CreateNewAssignment',
        'devilry_subjectadmin.view.guides.QualifiedForFinalExams',
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
    }, {
        ref: 'invalidPageMessage',
        selector: 'viewport guidesystemview #invalidPageMessage'
    }],

    init: function() {
        this.pointer = Ext.widget('guidesystem_pointer', {
            hidden: true
        });
        this.invalidPageTask = new Ext.util.DelayedTask(this._onInvalidPage, this);
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
        if(this._isVisible()) {
            this.getInvalidPageMessage().hide();

            // We assume that the user has navigated to a page outside the guide if
            // the guide uses more than 5 seconds to call setProgress().
            this.invalidPageTask.delay(5000);
        }
    },
    _onInvalidPage: function() {
        this._setNotLoading();
        this.getGuideView().getLayout().setActiveItem('invalidPageMessage');
    },

    setTitle: function(title) {
        this.getGuideView().setTitle(title);
    },

    setProgress: function(current, total) {
        this.invalidPageTask.cancel();
        this.getGuideView().getLayout().setActiveItem('main');
        this._setNotLoading();
        this.getProgress().update({
            current: current,
            total: total
        });
    },

    endGuide: function() {
        this.getGuideView().close();
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
