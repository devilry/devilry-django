Ext.require([
    'Ext.window.MessageBox'
]);
Ext.define('devilry_student.controller.BrowseHistory', {
    extend: 'Ext.app.Controller',

    requires: [
        'devilry_student.view.browsehistory.BrowsePeriods'
    ],

    views: [
        'browsehistory.Overview'
    ],

    refs: [{
        ref: 'overview',
        selector: 'viewport browsehistory'
    }, {
        ref: 'periodGrid',
        selector: 'viewport browsehistory browsehistory_periodgrid'
    }, {
        ref: 'assignmentGrid',
        selector: 'viewport browsehistory browsehistory_assignmentgrid'
    }, {
        ref: 'heading',
        selector: 'viewport browsehistory #heading'
    }],

    init: function() {
        this.control({
            'viewport browsehistory': {
                render: this._onRender
            },
            'viewport browsehistory browsehistory_periodgrid': {
                select: this._onSelectPeriod,
                allStoresLoadedSuccessfully: this._onAllPeriodStoresLoaded
            }
        });
    },

    _onRender: function() {
    },

    _selectPeriod: function(period_id) {
        var index = this.periodStore.findExact('id', parseInt(period_id, 10));
        if(index == -1) {
            Ext.MessageBox.show({
                title: gettext('Error'),
                msg: interpolate(gettext('Invalid %(period)s ID: %(period_id)s.'), {
                    period: gettext('period'),
                    period_id: period_id
                }, true),
                icon: Ext.MessageBox.ERROR,
                buttons: Ext.MessageBox.OK
            });
        } else {
            var selModel = this.getPeriodGrid().getSelectionModel();
            selModel.select(index);
        }
    },

    _onAllPeriodStoresLoaded: function(periodStore, relatedStudentKeyValueStore) {
        this.periodStore = periodStore;
        var period_id = this.getOverview().period_id;
        if(period_id) {
            this._selectPeriod(period_id);
        } else {
            this._onLoadNoneSelected();
        }
    },

    _onLoadNoneSelected: function() {
        this.application.setTitle(gettext('Browse'));
        this.application.breadcrumbs.set([], gettext('Browse'));
        var message = interpolate(gettext('Please select an %(assignment_term)s from the list.'), {
            assignment_term: gettext('assignment')
        }, true);
        this.getAssignmentGrid().getEl().mask(message, 'information-mask');
    },

    _onSelectPeriod: function(selModel, periodRecord) {
        var token = Ext.String.format('/browse/{0}', periodRecord.get('id'));
        this.application.route.setHashWithoutEvent(token);

        var path = [
            periodRecord.get('parentnode__short_name'),
            periodRecord.get('short_name')
        ].join('.');
        this.application.setTitle(path);
        this.application.breadcrumbs.set([{
            url: '#/browse/',
            text: gettext('Browse')
        }], path);

        this.getHeading().update({
            heading: periodRecord.get('parentnode__long_name'),
            subheading: path
        });
    }
});
