Ext.define('devilry_subjectadmin.controller.guides.QualifiedForFinalExams', {
    extend: 'devilry_subjectadmin.controller.guides.Base',

    views: [
        'guides.QualifiedForFinalExams'
    ],

    steps: 2,
    title: gettext('Qualified for final exams'),

    refs: [{
        ref: 'guideView',
        selector: 'viewport guide-qualifiedforfinalexams'
    }],


    init: function() {
        this.callParent(arguments);
        this.control({
            'viewport guide-qualifiedforfinalexams': {
                render: this.onRender
            },
            'viewport dashboard allactivewhereisadminlist': {
                render: this.ifActiveInterceptor(this.onFirstStep)
            },
            'viewport periodoverview': {
                render: this.ifActiveInterceptor(this._onPeriodRender)
            }
        });
    },

    onFirstStep: function() {
        this.getGuideView().getLayout().setActiveItem('dashboard');
        this.setStep('dashboard', 1);
    },

    _onPeriodRender: function() {
        this.setStep('period', 2);
    }
});
