/**
 * Base class for grids that needs an overview of an entire period.
 */
Ext.define('devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewGridBase', {
    extend: 'Ext.grid.Panel',
    cls: 'devilry_qualifiesforexam_previewgrid bootstrap',

    /**
     * @cfg {int} [firstAssignmentColumnIndex=1]
     * When rendering assignment result, we need to know the column index of the first assignment
     * to place the results in the correct column.
     */
    firstAssignmentColumnIndex: 1,

    /**
     * @cfg {bool} [hide_searchfield=false]
     * Hide the searchfield?
     */
    hide_searchfield: false,

    ignored_with_feedback_map: {},
    ignored_without_feedback_map: {},

    requires: [
        'Ext.XTemplate',
        'Ext.grid.column.Column',
        'devilry_subjectadmin.view.detailedperiodoverview.PeriodOverviewIgnoredMenu',
        'Ext.toolbar.TextItem'
    ],


    counterTpl: gettext('Showing {count} students'),

    studentColTpl: [
        '<div class="student" style="white-space: normal !important;">',
            '<div class="fullname">',
                '<tpl if="user.full_name">',
                    '<strong>{user.full_name}</strong>',
                '<tpl else>',
                    '<em>', gettext('Name missing'), '</em>',
                '</tpl>',
            '</div>',
            '<div class="username"><small class="muted">{user.username}</small></div>',
            '<tpl if="ignored_with_feedback">',
                '<span class="label label-important ignored_with_feedback-badge">',
                    gettext('Ignored, has feedback so this may be a problem'),
                '</span>',
            '</tpl>',
            '<tpl if="ignored_without_feedback">',
                '<span class="label label-info ignored_without_feedback-badge">',
                    gettext('Ignored, has no feedback so probably not a problem'),
                '</span>',
            '</tpl>',
        '</div>'
    ],
    feedbackColTpl: [
        '<div class="feedback feedback_assignment_{assignmentid}" style="white-space: normal !important;">',
            '<tpl if="grouplist.length == 0">',
                '<small class="text-error nofeedback">',
                    gettext('Not registered on assignment'),
                '</small>',
            '<tpl else>',
                '<tpl for="grouplist">',
                    '<div class="group-{id}">',
                        '<div class="status-{status}">',
                            '<tpl if="status === \'corrected\'">',
                                '<div class="{[this.getGradeClass(values.feedback.is_passing_grade)]}">',
                                    '<div class="passingstatus {[this.getTextClassForGrade(values.feedback.is_passing_grade)]}">',
                                        '{[this.getPassedOrFailedText(values.feedback.is_passing_grade)]}',
                                    '</div>',
                                    '<div class="gradedetails">',
                                        '<small class="grade muted">({feedback.grade})</small>',
                                        ' <small class="points muted">(',
                                            gettext('Points'),
                                            ':{feedback.points})',
                                        '</small>',
                                    '</div>',
                                '</div>',
                            '<tpl elseif="status === \'waiting-for-deliveries\'">',
                                '<em><small class="muted">', gettext('Waiting for deliveries'), '</small></em>',
                            '<tpl elseif="status === \'waiting-for-feedback\'">',
                                '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                            '<tpl else>',
                                '<span class="label label-important">{status}</span>',
                            '</tpl>',
                        '</div>',
                    '</div>',
                '</tpl>',
            '</tpl>',
        '</div>', {
            getGradeClass: function(is_passing_grade) {
                return is_passing_grade? 'passinggrade': 'notpassinggrade';
            },
            getTextClassForGrade: function(is_passing_grade) {
                return is_passing_grade? 'text-success': 'text-warning';
            },
            getPassedOrFailedText: function(is_passing_grade) {
                return is_passing_grade? gettext('Passed'): gettext('Failed');
            }
        }
    ],

    initComponent: function() {
        this.studentColTplCompiled = Ext.create('Ext.XTemplate', this.studentColTpl);
        this.feedbackColTplCompiled = Ext.create('Ext.XTemplate', this.feedbackColTpl);
        this.counterTplCompiled = Ext.create('Ext.XTemplate', this.counterTpl);
        this.columns = [{
            text: gettext('Student'),
            dataIndex: 'id',
            flex: 2,
            menuDisabled: true,
            minWidth: 200,
            sortable: false,
            renderer: Ext.bind(this.renderStudentColumn, this)
        }];
        this.setupColumns();
        this.setupToolbar();
        this.callParent(arguments);
        this.mon(this.getStore(), 'datachanged', this._onStoreDataChanged, this);
    },

    renderStudentColumn: function(value, meta, record) {
        return this.studentColTplCompiled.apply({
            user: record.get('user'),
            period_term: gettext('period'),
            ignored_with_feedback: this._isIgnoredWithFeedback(record),
            ignored_without_feedback: this._isIgnoredWithoutFeedback(record)
        });
    },


    /**
     * Override to add custom columns. Make sure you adjust ``firstAssignmentColumnIndex`` accordingly.
     */
    setupColumns: function() {
    },

    /** Override to customize toolbar */
    setupToolbar: function() {
        this.tbar = [{
            xtype: 'button',
            text: gettext('Sort'),
            itemId: 'sortButton',
            menu: [{
                itemId: 'sortByFullname',
                text: gettext('Full name'),
                listeners: {
                    scope: this,
                    click: this.sortByFullname
                }
            }, {
                itemId: 'sortByLastname',
                text: gettext('Last name'),
                listeners: {
                    scope: this,
                    click: this.sortByLastname
                }
            }, {
                itemId: 'sortByUsername',
                text: gettext('Username'),
                listeners: {
                    scope: this,
                    click: this.sortByUsername
                }
            }]
        }, '->', {
            xtype: 'button',
            text: 'Undefined',
            itemId: 'ignoredButton',
            hidden: true,
            menu: {
                xtype: 'periodoverviewignoredmenu',
                listeners: {
                    scope: this,
                    showButtonClick: this._onShowIgnored,
                    hideButtonClick: this._onHideIgnored
                }
            }
        }, {
            xtype: 'textfield',
            width: 250,
            emptyText: gettext('Search for name or username ...'),
            hidden: this.hide_searchfield,
            listeners: {
                scope: this,
                change: this._onSearch
            }
        }];
        this.bbar = ['->', {
            xtype: 'tbtext',
            text: gettext('Loading') + ' ...',
            itemId: 'itemCounter'
        }];
    },

    /**
     * Add assignment column to the grid.
     * @param assignment An object with assignment details.
     *
     * NOTE: Remember to call ``getView().refresh()`` on the grid after adding new dynamic columns.
     */
    addAssignmentResultColumn: function(assignment) {
        var column = Ext.create('Ext.grid.column.Column', {
            text: assignment.short_name,
            flex: 1,
            dataIndex: 'id',
            menuDisabled: true,
            sortable: false,
            minWidth: 150,
            renderer: Ext.bind(this._renderAssignmentResultColum, this)
        });
        this.headerCt.insert(this.columns.length, column);
    },

    /**
     * Loops through the given array and uses ``this.addAssignmentResultColumn()`` to add columns.
     * */
    addColumnForEachAssignment:function (assignments) {
        Ext.Array.each(assignments, function(assignment) {
            this.addAssignmentResultColumn(assignment);
        }, this);
        this.getView().refresh();
    },


    _renderAssignmentResultColum: function(value, meta, record, rowIndex, colIndex) {
        var assignmentIndex = colIndex - this.firstAssignmentColumnIndex;
        var assignmentinfo = record.get('groups_by_assignment')[assignmentIndex];
        return this.feedbackColTplCompiled.apply({
            grouplist: assignmentinfo.grouplist,
            assignmentid: assignmentinfo.assignmentid
        });
    },

    /**
     * Add sorters for the given assignments.
     * @param assignments An array of assignment-objects. Each object
     *   must have the ``short_name``-attribute, and the array must be sorted
     *   in the same order as they are in the records in the store.
     * */
    addAssignmentSorters: function(assignments) {
        var menu = this.down('#sortButton').menu;
        Ext.Array.each(assignments, function(assignment, index) {
            menu.add({
                text: assignment.short_name,
                hideOnClick: false,
                menu: [{
                    text: gettext('Sort by points ascending'),
                    listeners: {
                        scope: this,
                        click: function() {
                            this._onSortByFeedback(index, this._sortByPointsAscending);
                        }
                    }
                }, {
                    text: gettext('Sort by points decending'),
                    listeners: {
                        scope: this,
                        click: function() {
                            this._onSortByFeedback(index, this._sortByPointsDecending);
                        }
                    }
                }]
            });
        }, this);
    },


    _onSearch: function(field, newValue) {
        if(!Ext.isEmpty(this.searchtask)) {
            this.searchtask.cancel();
        }
        this.searchtask = new Ext.util.DelayedTask(function() {
            this._search(newValue.toLocaleLowerCase());
        }, this);
        this.searchtask.delay(140);
    },
    _searchMatch: function(searchString, value) {
        if(value === null) {
            value = gettext('Name missing'); // Allow users to search for this string to find users with missing name (this is the string they see when the name is missing)
        }
        return value.toLocaleLowerCase().indexOf(searchString) !== -1;
    },
    _search: function(searchString) {
        this.getStore().filterBy(function(record) {
            var user = record.get('user');
            return this._searchMatch(searchString, user.username) ||
                this._searchMatch(searchString, user.full_name);
        }, this);
    },


    _getBestFeedback: function(record, assignmentIndex) {
        var grouplist = record.get('groups_by_assignment')[assignmentIndex].grouplist;
        var bestFeedback = {
            points: -1,
            grade: '',
            is_passing_grade: false
        };
        for (var i = 0; i < grouplist.length; i++) {
            var group = grouplist[i];
            if(group.status === 'corrected' && group.feedback.points > bestFeedback.points) {
                bestFeedback = group.feedback;
            }
        }
        return bestFeedback;
    },
    _onSortByFeedback: function(assignmentIndex, sorter) {
        this.getStore().sort(Ext.create('Ext.util.Sorter', {
            sorterFn: Ext.bind(function(a, b) {
                var aFeedback = this._getBestFeedback(a, assignmentIndex);
                var bFeedback = this._getBestFeedback(b, assignmentIndex);
                return sorter(aFeedback, bFeedback);
            }, this)
        }));
    },
    _sortByPointsAscending: function(feedbackA, feedbackB) {
        return feedbackA.points - feedbackB.points;
    },
    _sortByPointsDecending: function(feedbackA, feedbackB) {
        return feedbackB.points - feedbackA.points;
    },


    sortByFullname: function() {
        this._sortByUser('fullname');
    },
    sortByLastname: function() {
        this._sortByUser('lastname');
    },
    sortByUsername: function() {
        this._sortByUser('username');
    },

    _sortByUser: function(sortby) {
        var sorter = null;
        if(sortby === 'username') {
            sorter = this._byUsernameCompare;
        } else if(sortby === 'fullname') {
            sorter = this._byFullnameCompare;
        } else if(sortby === 'lastname') {
            sorter = this._byLastnameCompare;
        } else {
            throw "Invalid sorter: " + sortby;
        }
        this.getStore().sort(Ext.create('Ext.util.Sorter', {
            sorterFn: Ext.bind(sorter, this)
        }));
    },

    _forceString:function (value) {
        if(value === null) {
            return '';
        } else {
            return value;
        }
    },

    _byUserPropertyCompare: function(a, b, property) {
        return this._forceString(a.get('user')[property]).localeCompare(this._forceString(b.get('user')[property]));
    },
    _byUsernameCompare: function (a, b) {
        return this._byUserPropertyCompare(a, b, 'username');
    },

    _byFullnameCompare: function (a, b) {
        return this._byUserPropertyCompare(a, b, 'full_name');
    },

    _getLastname: function(record) {
        var full_name = this._forceString(record.get('user').full_name);
        var splitted = full_name.split(/\s+/);
        return splitted[splitted.length-1];
    },
    _byLastnameCompare: function (a, b) {
        var aLastName = this._getLastname(a);
        var bLastName = this._getLastname(b);
        return aLastName.localeCompare(bLastName);
    },


    //
    //
    // Handle ignored
    //
    //

    _isIgnoredWithFeedback:function (record) {
        return typeof(this.ignored_with_feedback_map[record.get('user').id]) !== 'undefined';
    },
    _isIgnoredWithoutFeedback:function (record) {
        return typeof(this.ignored_without_feedback_map[record.get('user').id]) !== 'undefined';
    },
    _isIgnored:function (record) {
        return this._isIgnoredWithFeedback(record) || this._isIgnoredWithoutFeedback(record);
    },

    _hideIgnored:function () {
        var records = [];
        this.getStore().each(function (record) {
            if(this._isIgnored(record)) {
                records.push(record);
            }
        }, this);
        this.getStore().remove(records);
    },
    _showIgnored:function () {
        this.getStore().loadData(this.ignored_with_feedback, true);
        this.getStore().loadData(this.ignored_without_feedback, true);
    },

    _onShowIgnored:function (menu) {
        this._showIgnored();
    },
    _onHideIgnored:function (menu) {
        this._hideIgnored();
    },

    _byUserId: function (aggregatedStudentInfoArray) {
        var byUserId = {};
        for (var i = 0; i < aggregatedStudentInfoArray.length; i++) {
            var aggregatedStudentInfo = aggregatedStudentInfoArray[i];
            byUserId[aggregatedStudentInfo.user.id] = aggregatedStudentInfo;
        }
        return byUserId;
    },

    handleIgnored: function (period_id, ignored_with_feedback, ignored_without_feedback) {
        if((ignored_with_feedback.length + ignored_without_feedback.length) === 0) {
            return;
        }

        // Turn into map for the rendering function
        this.ignored_with_feedback_map = this._byUserId(ignored_with_feedback);
        this.ignored_without_feedback_map = this._byUserId(ignored_without_feedback);
        this.ignored_with_feedback = ignored_with_feedback;
        this.ignored_without_feedback = ignored_without_feedback;

        // Show the ignoredButton
        var labelTpl = Ext.create('Ext.XTemplate',
            gettext('Some students are ignored'),
            '<span class="bootstrap">',
                '<tpl if="ignored_with_feedback_count">',
                ' <span class="badge badge-important">{ignored_with_feedback_count}</span>',
                '</tpl>',
                '<tpl if="ignored_without_feedback_count">',
                    ' <span class="badge badge-info">{ignored_without_feedback_count}</span>',
                '</tpl>',
            '</span>'
        );
        var ignoredButton = this.down('#ignoredButton');
        ignoredButton.setText(labelTpl.apply({
            ignored_with_feedback_count: ignored_with_feedback.length,
            ignored_without_feedback_count: ignored_without_feedback.length
        }));
        ignoredButton.menu.updateBody({
            period_id: period_id,
            ignored_with_feedback_count: ignored_with_feedback.length,
            ignored_without_feedback_count: ignored_without_feedback.length
        });
        ignoredButton.show();
    },


    _onStoreDataChanged:function () {
        this.updateCounter();
    },
    updateCounter:function () {
        var itemCounter = this.down('#itemCounter');
        var store = this.getStore();
        var label = this.counterTplCompiled.apply({
            count: store.count()
        });
        itemCounter.setText(label);
    }
});
