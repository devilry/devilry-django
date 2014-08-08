Ext.define('devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewIgnoredMenu', {
    extend: 'Ext.menu.Menu',
    alias: 'widget.periodoverviewignoredmenu',
    cls: 'devilry_subjectadmin',

    ignoredHidden: true,

    bodyTpl: [
        '<tpl if="!loading">',
            '<p>',
                gettext('Some students are registered on groups within this {period_term}, but are not registered on the {period_term}. It is common to remove students from the {period_term} when they quit the {subject_term}, so this may not indicate a problem.'),
            '</p>',
            '<ul class="unstyled">',
                '<li>',
                    '<span class="badge badge-important">{ignored_with_feedback_count}</span> ',
                    '<small>',
                        gettext('Students in groups with feedback and not registered on the {period_term}.'),
                    '</small>',
                '</li>',
                '<li>',
                    '<span class="badge badge-info">{ignored_without_feedback_count}</span> ',
                    '<small>',
                        gettext('Students in groups without feedback but not registered on the {period_term}.'),
                    '</small>',
                '</li>',
            '</ul>',
            '<tpl if="ignoredHidden">',
                '<a class="btn btn-small btn-success showhidebutton show-ignored-button">',
                    '<i class="icon-white icon-plus"></i> ',
                    gettext('Show ignored students in the table'),
                '</a>',
            '<tpl else>',
                '<a class="btn btn-small btn-inverse showhidebutton hide-ignored-button">',
                    '<i class="icon-white icon-minus"></i> ',
                    gettext('Hide ignored students in the table'),
                '</a>',
            '</tpl>',

            ' &nbsp;<a class="new-window-link" href="{manageRelatedStudentsUrl}" target="_blank">',
                gettext('Edit/view students on the {period_term}'),
            '</a>',
        '</tpl>'
    ],

    initComponent: function() {
        this.addEvents([
            /**
             * @event
             * Triggered when the show ignored students button is clicked.
             */
            'showButtonClick',

            /**
             * @event
             * Triggered when the hide ignored students button is clicked.
             */
            'hideButtonClick'
        ]);

        Ext.apply(this, {
            plain: true,
            maxWidth: 550,
            layout: 'anchor',
            items: [{
                xtype: 'box',
                padding: 10,
                cls: 'bootstrap',
                anchor: '100%',
                itemId: 'body',
                tpl: this.bodyTpl,
                style: 'white-space: normal !important;',
                data: {
                    loading: true
                },
                listeners: {
                    scope: this,
                    click: {
                        element: 'el',
                        delegate: 'a.showhidebutton',
                        fn: this._onClickShowOrHideButton
                    }
                }
            }]
        });
        this.callParent(arguments);
    },


    _updateBody:function () {
        this.down('#body').update(this.templatedata);
    },


    _onClickShowOrHideButton:function (e) {
        e.preventDefault();
        var element = Ext.get(e.target);
        this.hide();
        if(element.hasCls('hide-ignored-button')) {
            this._onClickHideButton();
        } else {
            this._onClickShowButton();
        }
        this._updateBody();
    },
    _onClickShowButton:function (e) {
        this.fireEvent('showButtonClick', this);
        this.templatedata.ignoredHidden = false;
    },
    _onClickHideButton:function (e) {
        this.fireEvent('hideButtonClick', this);
        this.templatedata.ignoredHidden = true;
    },

    updateBody:function (data) {
        this.templatedata = {
            loading: false,
            ignoredHidden: this.ignoredHidden,
            period_term: gettext('period'),
            manageRelatedStudentsUrl: devilry_subjectadmin.utils.UrlLookup.manageRelatedStudents(
                data.period_id),
            subject_term: gettext('subject')
        };
        Ext.apply(this.templatedata, data);
        this._updateBody();
    }
});
