/**
 * Controller for the select buttons and select by search field.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.Select', {
    extend: 'Ext.app.Controller',
    
    views: [
        'managestudents.ListOfGroups'
    ],

    requires: [
        'Ext.util.KeyMap',
        'Ext.util.MixedCollection',
        'Ext.XTemplate'
    ],

    stores: [
        'Groups'
    ],

    sharedData: Ext.define('sharedData', { 
        singleton: true,
        removeFromSelectionMode: false, 
    }) ,
    /**
     * Get the main view for managestudents.
     * @return {devilry_subjectadmin.view.managestudents.Overview} The overview.
     * @method getOverview
     */

    refs: [{
        ref: 'listOfGroups',
        selector: 'listofgroups'
    }],

    init: function() {
        this.labelWithGroupCountTpl = new Ext.XTemplate(
            gettext('{label} (Matching groups: {groupcount})')
        );
        this.control({
            'viewport managestudentsoverview listofgroups': {
                render: this._onRenderListOfGroups
            },

            'viewport managestudentsoverview #selectall': {
                click: this._onSelectAll
            },
            'viewport managestudentsoverview #deselectall': {
                click: this._onDeselectAll
            },
            'viewport managestudentsoverview #invertselection': {
                click: this._onInvertselection
            },
            
            // NOTE: The listeners below are shared by items in both
            //       #replaceSelectionMenu and #addToSelectionMenu.
            //       We use the itemId of their menu to determine if we want to
            //       keepExisting or not. See _isInAddToSelectionMenu()

            // By status
            'viewport managestudentsoverview #selectStatusOpen': {
                click: this._onSelectStatusOpen
            },
            'viewport managestudentsoverview #selectStatusClosed': {
                click: this._onSelectStatusClosed
            },

            // By feedback
            'viewport managestudentsoverview #selectGradeFailed': {
                click: this._onSelectGradeFailed
            },
            'viewport managestudentsoverview #selectGradePassed': {
                click: this._onSelectGradePassed
            },
            'viewport managestudentsoverview #selectNoFeedback': {
                click: this._onSelectNoFeedback
            },
            'viewport managestudentsoverview #selectHasFeedback': {
                click: this._onSelectHasFeedback
            },
            'viewport managestudentsoverview #specificGradeMenu': {
                show: this._onShowSpecificGradeMenu
            },
            'viewport managestudentsoverview #specificGradeMenu menuitem': {
                click: this._onSpecificGradeMenuItemClick
            },
            'viewport managestudentsoverview #specificPointsMenu': {
                show: this._onShowSpecificPointsMenu
            },
            'viewport managestudentsoverview #specificPointsMenu menuitem': {
                click: this._onSpecificPointsMenuItemClick
            },

            // By deliveries
            'viewport managestudentsoverview #selectHasDeliveries': {
                click: this._onSelectHasDeliveries
            },
            'viewport managestudentsoverview #selectNoDeliveries': {
                click: this._onSelectNoDeliveries
            },
            'viewport managestudentsoverview #specificNumDeliveriesMenu': {
                show: this._onShowSpecificNumDeliveriesMenu
            },
            'viewport managestudentsoverview #specificNumDeliveriesMenu menuitem': {
                click: this._onSpecificNumDeliveriesMenuItemClick
            },

            // By examiners
            'viewport managestudentsoverview #selectHasExaminer': {
                click: this._onSelectHasExaminer
            },
            'viewport managestudentsoverview #selectNoExaminer': {
                click: this._onSelectNoExaminer
            },
            'viewport managestudentsoverview #specificExaminerMenu': {
                show: this._onShowSpecificExaminerMenu
            },
            'viewport managestudentsoverview #specificExaminerMenu menuitem': {
                click: this._onSpecificExaminerMenuItemClick
            },

            // By tags
            'viewport managestudentsoverview #selectHasTag': {
                click: this._onSelectHasTag
            },
            'viewport managestudentsoverview #selectNoTag': {
                click: this._onSelectNoTag
            },
            'viewport managestudentsoverview #specificTagMenu': {
                show: this._onShowSpecificTagMenu
            },
            'viewport managestudentsoverview #specificTagMenu menuitem': {
                click: this._onSpecificTagMenuItemClick
            }
        });
    },

    _onRenderListOfGroups: function() {
        var map = new Ext.util.KeyMap(this.getListOfGroups().getEl(), {
            key: 'a',
            ctrl: true,
            fn: this._onSelectAll,
            scope: this
        });
    },

    _intCompare: function(a, b) {
        if(a < b)
            return -1;
        else if(a > b)
            return 1;
        else
            return 0;
    },



    /***********************************************
     *
     * Select menu button handlers
     *
     **********************************************/

    _onSelectAll: function() {
        this.getListOfGroups().getSelectionModel().selectAll();
    },
    _onDeselectAll: function() {
        this.getListOfGroups().getSelectionModel().deselectAll();
    },
    _onInvertselection: function() {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        var selected = Ext.clone(selectionModel.selected.items);

        // Add listener to the "next" selectionchange event, and trigger the selectionchange with selectAll
        this.getListOfGroups().on({
            selectionchange: function() {
                this._deselectGroupRecords(selected);
            },
            scope: this,
            single: true
        });
        this.getListOfGroups().getSelectionModel().selectAll();
    },


    // _isInAddToSelectionMenu: function(button) {
    //     return button.up('#replaceSelectionMenu') === undefined;
    // },


    _isInAddToSelectionMenu: function(button) {
        
        if(button.up('#removeFromSelectionMenu')) {
            sharedData.removeFromSelectionMode = true;
        }

        if((button.up('#replaceSelectionMenu') === undefined) && (button.up('#removeFromSelectionMenu') === undefined)) {
            return true;
        }
        return false;
    },


    // 
    // Status
    //

    _onSelectStatusOpen: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('is_open') === true;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectStatusClosed: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('is_open') === false;
        }, this, this._isInAddToSelectionMenu(button));
    },


    //
    // Grade
    //

    _onSelectGradeFailed: function(button) {
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback && !feedback.is_passing_grade;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectGradePassed: function(button) {
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback && feedback.is_passing_grade;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onSelectHasFeedback: function(button) {
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback !== null;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onSelectNoFeedback: function(button) {
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback === null;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificGradeMenu: function(menu) {
        // Add unique grades, and count groups
        var gradeMap = new Ext.util.MixedCollection(); // grade -> {grade: grade, count: COUNT}
        this.getGroupsStore().each(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            if(feedback) {
                var grade = feedback.grade;
                if(gradeMap.containsKey(grade)) {
                    gradeMap.get(grade).count ++;
                } else {
                    gradeMap.add(grade, {
                        grade: grade,
                        points: feedback.points,
                        count: 1
                    });
                }
            }
        }, this);
        
        // Sort
        // NOTE: Using points for sorting since sorting by grade do not work well for grades like 12/24
        var me = this;
        gradeMap.sortBy(function(a, b) {
            return me._intCompare(a.points, b.points);
        });

        // Create and set items
        var items = [];
        gradeMap.each(function(grade) {
            items.push({
                feedback_grade: grade.grade,
                text: grade.grade
                //text: this.labelWithGroupCountTpl.apply({
                    //label: grade.grade,
                    //groupcount: grade.count
                //})
            });
        }, this);
        menu.setItems(items);
    },

    _onSpecificGradeMenuItemClick: function(button) {
        var grade = button.feedback_grade;
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback && feedback.grade == grade;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificPointsMenu: function(menu) {
        // Add unique pointss, and count groups
        var pointsMap = new Ext.util.MixedCollection(); // points -> {points: points, count: COUNT}
        this.getGroupsStore().each(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            if(feedback) {
                var points = feedback.points;
                if(pointsMap.containsKey(points)) {
                    pointsMap.get(points).count ++;
                } else {
                    pointsMap.add(points, {
                        points: points,
                        count: 1
                    });
                }
            }
        }, this);
        
        // Sort
        var me = this;
        pointsMap.sortBy(function(a, b) {
            return me._intCompare(a.points, b.points);
        });

        // Create and set items
        var items = [];
        pointsMap.each(function(points) {
            items.push({
                feedback_points: points.points,
                text: points.points
                //text: this.labelWithGroupCountTpl.apply({
                    //label: points.points,
                    //groupcount: points.count
                //})
            });
        }, this);
        menu.setItems(items);
    },

    _onSpecificPointsMenuItemClick: function(button) {
        var points = button.feedback_points;
        this._selectBy(function(groupRecord) {
            var feedback = groupRecord.get('feedback');
            return feedback && feedback.points == points;
        }, this, this._isInAddToSelectionMenu(button));
    },


    // 
    // Deliveries
    //

    _onSelectHasDeliveries: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('num_deliveries') > 0;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectNoDeliveries: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('num_deliveries') === 0;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificNumDeliveriesMenu: function(menu) {
        // Add unique num_deliveriess, and count groups
        var num_deliveriesMap = {}; // NUMDELIVERIES -> true
        this.getGroupsStore().each(function(groupRecord) {
            var num_deliveries = groupRecord.get('num_deliveries');
            num_deliveriesMap[num_deliveries] = true;
        }, this);
        
        // Sort
        var num_deliveriesArray = Ext.Object.getKeys(num_deliveriesMap);
        num_deliveriesArray = Ext.Array.sort(num_deliveriesArray);

        // Create and set items
        var items = [];
        Ext.Array.each(num_deliveriesArray, function(num_deliveries) {
            items.push({
                num_deliveries: num_deliveries,
                text: Ext.String.format('{0}', num_deliveries)
            });
        }, this);
        menu.setItems(items);
    },

    _onSpecificNumDeliveriesMenuItemClick: function(button) {
        var num_deliveries = button.num_deliveries;
        this._selectBy(function(groupRecord) {
            return groupRecord.get('num_deliveries') == num_deliveries;
        }, this, this._isInAddToSelectionMenu(button));
    },


    //
    // Examiners
    //

    _onSelectHasExaminer: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('examiners').length > 0;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectNoExaminer: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('examiners').length === 0;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificExaminerMenu: function(menu) {
        // Add unique users, and count groups
        var examinerMap = new Ext.util.MixedCollection(); // userid -> {user: userObj, count: COUNT, name: NAME}
        this.getGroupsStore().each(function(groupRecord) {
            var examiners = groupRecord.get('examiners');
            for(var index=0; index<examiners.length; index++)  {
                var examiner = examiners[index];
                var userid = examiner.user.id;
                if(examinerMap.containsKey(userid)) {
                    examinerMap.get(userid).count ++;
                } else {
                    var name = examiner.user.full_name || examiner.user.username || Ext.String.format('User ID: ', examiner.user.id);
                    examinerMap.add(userid, {
                        user: examiner.user,
                        name: name,
                        count: 1
                    });
                }
            }
        }, this);
        
        // Sort
        examinerMap.sortBy(function(a, b) {
            return a.name.localeCompare(b.name);
        });

        // Create and set items
        var items = [];
        examinerMap.each(function(examiner) {
            items.push({
                examinerUserId: examiner.user.id,
                text: this.labelWithGroupCountTpl.apply({
                    label: examiner.name,
                    groupcount: examiner.count
                })
            });
        }, this);
        menu.setItems(items);
    },

    _onSpecificExaminerMenuItemClick: function(button) {
        var userid = button.examinerUserId;
        this._selectBy(function(groupRecord) {
            return groupRecord.hasExaminer(userid);
        }, this, this._isInAddToSelectionMenu(button));
    },



    //
    //Tags
    //

    _onSelectHasTag: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('tags').length > 0;
        }, this, this._isInAddToSelectionMenu(button));
    },
    _onSelectNoTag: function(button) {
        this._selectBy(function(groupRecord) {
            return groupRecord.get('tags').length === 0;
        }, this, this._isInAddToSelectionMenu(button));
    },

    _onShowSpecificTagMenu: function(menu) {
        // Add unique tags, and count groups
        var tagMap = new Ext.util.MixedCollection(); // TAG -> {tag: TAG, count: COUNT}
        this.getGroupsStore().each(function(groupRecord) {
            var tags = groupRecord.get('tags');
            for(var index=0; index<tags.length; index++)  {
                var tagObj = tags[index];
                if(tagMap.containsKey(tagObj.tag)) {
                    tagMap.get(tagObj.tag).count ++;
                } else {
                    tagMap.add(tagObj.tag, {
                        tag: tagObj.tag,
                        count: 1
                    });
                }
            }
        }, this);
        
        // Sort
        tagMap.sortBy(function(a, b) {
            return a.tag.localeCompare(b.tag);
        });

        // Create and set items
        var items = [];
        tagMap.each(function(tag) {
            items.push({
                tagString: tag.tag,
                text: tag.tag
                //text: this.labelWithGroupCountTpl.apply({
                    //label: tag.tag,
                    //groupcount: tag.count
                //})
            });
        });
        menu.setItems(items);
    },

    _onSpecificTagMenuItemClick: function(button) {
        var tag = button.tagString;
        this._selectBy(function(groupRecord) {
            return groupRecord.hasTag(tag);
        }, this, this._isInAddToSelectionMenu(button));
    },






    /***************************************************
     *
     * Methods to simplify selecting users
     *
     **************************************************/

    _findGroupRecordsBy: function(fn, scope) {
        var groupRecords = [];
        this.getGroupsStore().each(function(groupRecord) {
            var match = Ext.bind(fn, scope)(groupRecord);
            if(match) {
                groupRecords.push(groupRecord);
            }
        }, this);
        return groupRecords;
    },

    _selectBy: function(fn, scope, keepExisting) {
      var groupRecords = this._findGroupRecordsBy(fn, scope);

      if(sharedData.removeFromSelectionMode){
        this._deselectGroupRecords(groupRecords);
        sharedData.removeFromSelectionMode = false;
      } else {
        this._selectGroupRecords(groupRecords, keepExisting);
      }

    },

    /** Select the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * @param {Boolean} [keepExisting=false] True to retain existing selections
     * */
    _selectGroupRecords: function(groupRecords, keepExisting) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.select(groupRecords, keepExisting);
    },

    /** Deselect the given group records.
     * @param {[devilry_subjectadmin.model.Group]} [groupRecords] Group records array.
     * */
    _deselectGroupRecords: function(groupRecords) {
        var selectionModel = this.getListOfGroups().getSelectionModel();
        selectionModel.deselect(groupRecords);
    },

    /** Get group record by group id.
     * @param {int} [groupId] The group id.
     * @return {devilry_subjectadmin.model.Group} The group record, or ``undefined`` if it is not found.
     * */
    _getGroupRecordById: function(groupId) {
        var index = this.getGroupsStore().findExact('id', groupId);
        if(index == -1) {
            return undefined;
        }
        return this.getGroupsStore().getAt(index);
    }

    /** Return ``true`` if ``groupRecord`` is selected. */
    //_groupRecordIsSelected: function(groupRecord) {
        //return this.getListOfGroups().getSelectionModel().isSelected(groupRecord);
    //}
});
