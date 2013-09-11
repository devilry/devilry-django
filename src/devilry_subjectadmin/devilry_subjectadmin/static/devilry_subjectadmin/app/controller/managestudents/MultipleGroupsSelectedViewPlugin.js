/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a multiple groups when
 * they are selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.MultipleGroupsSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    views: [
        'managestudents.MultipleGroupsSelectedView',
        'managestudents.SelectedGroupsSummaryGrid'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage',
        'devilry_extjsextras.EvenRandomSelection',
        'devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup',
        'Ext.tip.ToolTip',
        'Ext.util.KeyNav'
    ],

    stores: ['SelectedGroups'],

    models: [
        'MergeIntoGroup'
    ],


    random_distribute_result_tpl: [
        '<h3>',
            gettext('Examiners random distributed successfully'),
        '</h3>',
        '<dl>',
        '<tpl for="resultsByExaminer">',
            '<dt>{examiner}</dt>',
            '<dd>',
                '{groupRecords.length}',
            '</dd>',
        '</tpl>',
        '</dl>'
    ],


    group_summarygrid_size_cookiename: 'devilry_subjectadmin.managestudents.MultipleGroupsSelectedViewPlugin.groupsummary.height',
    group_summarygrid_collapse_cookiename: 'devilry_subjectadmin.managestudents.MultipleGroupsSelectedViewPlugin.groupsummary.collapse',

    refs: [{
        ref: 'scrollableBodyContainer',
        selector: 'multiplegroupsview #scrollableBodyContainer'
    }, {
        ref: 'viewport',
        selector: 'viewport'

    // Examiners
    }, {
        ref: 'manageExaminers',
        selector: 'viewport multiplegroupsview manageexaminersonmultiple'
    }, {
        ref: 'manageExaminersCardBody',
        selector: 'viewport multiplegroupsview manageexaminersonmultiple #cardBody'
    }, {
        ref: 'setExaminersGrid',
        selector: 'viewport multiplegroupsview manageexaminersonmultiple #setExaminersPanel selectexaminersgrid'
    }, {
        ref: 'randomDistributeExaminersGrid',
        selector: 'viewport multiplegroupsview manageexaminersonmultiple #randomDistributeExaminersPanel selectexaminersgrid'
    }, {
        ref: 'addExaminersGrid',
        selector: 'viewport multiplegroupsview manageexaminersonmultiple #addExaminersPanel selectexaminersgrid'

    // Tags
    }, {
        ref: 'manageTags',
        selector: 'viewport multiplegroupsview managetagsonmultiple'
    }, {
        ref: 'manageTagsCardBody',
        selector: 'viewport multiplegroupsview managetagsonmultiple #manageTagsCardBody'

    // Merge
    }, {
        ref: 'mergeGroups',
        selector: 'multiplegroupsview mergegroups'
    }, {
        ref: 'confirmMergeGroupsContainer',
        selector: 'multiplegroupsview #confirmMergeGroupsContainer'
    }, {
        ref: 'mergeGroupsHelp',
        selector: 'multiplegroupsview #mergeGroupsHelp'
    }, {
        ref: 'mergeGroupsButton',
        selector: 'multiplegroupsview #mergeGroupsButton'
    }, {
        ref: 'mergeGroupsConfirmButton',
        selector: 'multiplegroupsview #mergeGroupsConfirmButton'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsMultipleGroupsSelected: this._onMultipleGroupsSelected,
            managestudentsGroupSorterChanged: this._onGroupsSorterChanged
        });
        this.control({
            'viewport multiplegroupsview selectedgroupssummarygrid': {
                resize: this._onGroupSummaryGridResize,
                collapse: this._onGroupSummaryGridCollapse,
                expand: this._onGroupSummaryGridExpand,
                boxready: this._onGroupsSummaryBoxReady
            },

            // moreinfobox
            'viewport multiplegroupsview moreinfobox': {
                moreclick: this._onMoreClick,
                lessclick: this._onLessClick
            },


            // setExaminers
            'viewport multiplegroupsview manageexaminersonmultiple #setExaminersButton': {
                click: this._onSetExaminers
            },
            'viewport multiplegroupsview manageexaminersonmultiple okcancelpanel#setExaminersPanel': {
                cancel: this._showExaminersDefaultView,
                ok: this._onSetExaminersConfirmed
            },

            // randomDistributeExaminers
            'viewport multiplegroupsview manageexaminersonmultiple #randomDistributeExaminersButton': {
                click: this._onRandomDistributeExaminers
            },
            'viewport multiplegroupsview manageexaminersonmultiple okcancelpanel#randomDistributeExaminersPanel': {
                cancel: this._showExaminersDefaultView,
                ok: this._onRandomDistributeExaminersConfirmed
            },

            // addExaminers
            'viewport multiplegroupsview manageexaminersonmultiple #addExaminersButton': {
                click: this._onAddExaminers
            },
            'viewport multiplegroupsview manageexaminersonmultiple okcancelpanel#addExaminersPanel': {
                cancel: this._showExaminersDefaultView,
                ok: this._onAddExaminersConfirmed
            },

            // clearExaminers
            'viewport multiplegroupsview manageexaminersonmultiple #clearExaminersButton': {
                click: this._onClearExaminers
            },
            'viewport multiplegroupsview manageexaminersonmultiple okcancelpanel#clearExaminersPanel': {
                cancel: this._showExaminersDefaultView,
                ok: this._onClearExaminersConfirmed
            },


            // setTags
            'viewport multiplegroupsview #setTagsButton': {
                click: this._onSetTags
            },
            'viewport multiplegroupsview choosetagspanel#setTagsPanel': {
                cancel: this._showTagsDefaultView,
                savetags: this._onSetTagsSave
            },

            // addTags
            'viewport multiplegroupsview #addTagsButton': {
                click: this._onAddTags
            },
            'viewport multiplegroupsview choosetagspanel#addTagsPanel': {
                cancel: this._showTagsDefaultView,
                savetags: this._onAddTagsSave
            },

            // clearTags
            'viewport multiplegroupsview #clearTagsButton': {
                click: this._onClearTags
            },
            'viewport multiplegroupsview okcancelpanel#clearTagsPanel': {
                cancel: this._showTagsDefaultView,
                ok: this._onClearTagsConfirmed
            },


            // Merge groups
            'viewport multiplegroupsview #mergeGroupsButton': {
                click: this._onMergeGroupsButton
            },
            'viewport multiplegroupsview #mergeGroupsCancelButton': {
                click: this._onMergeGroupsCancel
            },
            'viewport multiplegroupsview #mergeGroupsConfirmButton': {
                click: this._onMergeGroupsConfirm
            },

            // Delete
            'viewport multiplegroupsview #multiDeleteButton': {
                click: this._onDelete
            }
        });

        this.mon(this.getMergeIntoGroupModel().proxy, {
            scope: this,
            exception: this._onMergeIntoGroupProxyError
        });
    },

    _onGroupsSorterChanged: function(sorter) {
        var store = this.getSelectedGroupsStore();
        store.sortBySpecialSorter(sorter);
    },

    _onMultipleGroupsSelected: function(manageStudentsController, groupRecords) {
        this._fadeOut(this.getScrollableBodyContainer());
        this._closeAllEditors();
        this.groupRecords = groupRecords;
        this.manageStudentsController = manageStudentsController;
        this._setPeriodIdOnExaminerManager();
        this.manageStudentsController.setBodyCard('multiplegroupsSelected');
        this._populateSelectedGroupsStore();
        this._fadeIn(this.getScrollableBodyContainer());
    },

    _fadeOut: function(component) {
        component.getEl().setOpacity(0.2);
    },

    _fadeIn: function(component) {
        component.getEl().animate({
            duration: 400,
            from: {opacity: 0.1},
            to: {opacity: 1.0}
        });
    },

    _setPeriodIdOnExaminerManager: function() {
        this.getManageExaminers().setPeriodId(this.manageStudentsController.assignmentRecord.get('parentnode'));
    },

    _closeAllEditors: function() {
        this._showExaminersDefaultView();
        this._showMergeGroupsDefaultView();
        this._showTagsDefaultView();
    },

    _populateSelectedGroupsStore: function() {
        var store = this.getSelectedGroupsStore();
        //Ext.Array.each(this.groupRecords, function(groupRecord, index) {
            //console.log(groupRecord, 'loaded');
            //store.add(groupRecord);
        //}, this);
        store.removeAll();
        store.loadData(this.groupRecords);
        store.sortBySpecialSorter(this.manageStudentsController.getCurrentGroupsStoreSorter());
    },

    _scrollIntroView: function(widget) {
        widget.getEl().scrollIntoView(this.getScrollableBodyContainer().getEl(), false, true);
    },

    _onMoreClick: function(moreinfobox) {
        this._scrollIntroView(moreinfobox);
    },
    _onLessClick: function(moreinfobox) {
        this._scrollIntroView(moreinfobox);
    },

    _onGroupSummaryGridResize: function(groupsummarygrid, width, height, oldWidth, oldHeight) {
        var maxHeight = this.getViewport().getHeight() - 120;
        if(height > maxHeight) {
            groupsummarygrid.setHeight(maxHeight);
        } else {
            var firstLoad = Ext.isEmpty(oldHeight);
            if(!firstLoad) {
                Ext.util.Cookies.set(this.group_summarygrid_size_cookiename, height);
            }
        }
    },

    _onGroupSummaryGridCollapse: function() {
        Ext.util.Cookies.set(this.group_summarygrid_collapse_cookiename, 'collapsed');
    },
    _onGroupSummaryGridExpand: function() {
        Ext.util.Cookies.set(this.group_summarygrid_collapse_cookiename, 'expanded');
    },

    _onGroupsSummaryBoxReady: function(groupsummarygrid) {
        var height = Ext.util.Cookies.get(this.group_summarygrid_size_cookiename);
        var collapseOrExpanded = Ext.util.Cookies.get(this.group_summarygrid_collapse_cookiename);
        if(collapseOrExpanded === 'expanded') {
            groupsummarygrid.expand();
        }
        if(height) {
            groupsummarygrid.setHeight(parseInt(height, 10));
        }
    },


    /************************************************
     *
     * Set examiners
     *
     ************************************************/

    _scrollExaminersIntoView: function() {
        this._scrollIntroView(this.getManageExaminers());
    },
    _showExaminersDefaultView: function() {
        this.getManageExaminersCardBody().getLayout().setActiveItem('helpAndButtonsContainer');
    },

    _syncExaminers: function(userStore, doNotDeleteUsers) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            var userRecords = userStore.data.items;
            devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeExaminers({
                groupRecord: groupRecord,
                userRecords: userRecords,
                doNotDeleteUsers: doNotDeleteUsers
            });
        }
    },

    // Set examiners
    _onSetExaminers: function() {
        this.getManageExaminersCardBody().getLayout().setActiveItem('setExaminersPanel');
        this._scrollExaminersIntoView();
    },
    _onSetExaminersConfirmed: function() {
        var grid = this.getSetExaminersGrid();
        var userStore = grid.getSelectedAsUserStore();
        this._syncExaminers(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                // TODO: Notify user about success
            }
        }, {
            examinersOnly: true
        });
    },

    // Random distribute examiners
    _onRandomDistributeExaminers: function() {
        this.getManageExaminersCardBody().getLayout().setActiveItem('randomDistributeExaminersPanel');
        this._scrollExaminersIntoView();
    },
    _syncExaminersRandomly: function(userStore) {
        var randomExaminerPool = Ext.create('devilry_extjsextras.EvenRandomSelection', {
            selection: userStore.data.items
        });
        var resultsByExaminer = {};
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            var examinerUserRecord = randomExaminerPool.getRandomItem();
            devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeExaminers({
                groupRecord: groupRecord,
                userRecords: [examinerUserRecord],
                doNotDeleteUsers: false
            });

            // Add to results
            var displayName = examinerUserRecord.getDisplayName();
            if(Ext.isEmpty(resultsByExaminer[displayName])) {
                resultsByExaminer[displayName] = [];
            }
            resultsByExaminer[displayName].push(groupRecord);
        }
        return resultsByExaminer;
    },
    _onRandomDistributeExaminersConfirmed: function() {
        var grid = this.getRandomDistributeExaminersGrid();
        var userStore = grid.getSelectedAsUserStore();
        var resultsByExaminer = this._syncExaminersRandomly(userStore);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                this._onRandomDistributeExaminersSuccess(resultsByExaminer);
            }
        }, {
            examinersOnly: true
        });
    },
    _onRandomDistributeExaminersSuccess: function(resultsByExaminer) {
        var resultsAsArray = [];
        Ext.Object.each(resultsByExaminer, function(examiner, groupRecords) {
            resultsAsArray.push({
                examiner: examiner,
                groupRecords: groupRecords
            });
        }, this);
        var message = Ext.create('Ext.XTemplate', this.random_distribute_result_tpl).apply({
            resultsByExaminer: resultsAsArray
        });
        this.application.getAlertmessagelist().add({
            type: 'success',
            autoclose: true,
            message: message
        });
    },

    // Add examiners
    _onAddExaminers: function() {
        this.getManageExaminersCardBody().getLayout().setActiveItem('addExaminersPanel');
        this._scrollExaminersIntoView();
    },
    _onAddExaminersConfirmed: function() {
        var grid = this.getAddExaminersGrid();
        var userStore = grid.getSelectedAsUserStore();
        this._syncExaminers(userStore, true);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
                // TODO: Notify user about successs
            }
        }, {
            examinersOnly: true
        });
    },

    // Clear examiners
    _onClearExaminers: function() {
        this.getManageExaminersCardBody().getLayout().setActiveItem('clearExaminersPanel');
        this._scrollExaminersIntoView();
    },
    _onClearExaminersConfirmed: function() {
        Ext.Array.each(this.groupRecords, function(groupRecord) {
            groupRecord.set('examiners', []);
        }, this);
        this.manageStudentsController.notifyMultipleGroupsChange({
        }, {
            examinersOnly: true
        });
    },




    /************************************************
     *
     * Set tags
     *
     ************************************************/
    _scrollTagsIntoView: function() {
        this._scrollIntroView(this.getManageTags());
    },

    _syncTags: function(sourceTags, doNotDeleteTags) {
        for(var index=0; index<this.groupRecords.length; index++)  {
            var groupRecord = this.groupRecords[index];
            devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeTags({
                groupRecord: groupRecord,
                sourceTags: sourceTags,
                doNotDeleteTags: doNotDeleteTags
            });
        }
    },


    // Set tags
    _onSetTags: function() {
        this.getManageTagsCardBody().getLayout().setActiveItem('setTagsPanel');
        this._scrollTagsIntoView();
    },
    _onSetTagsSave: function(win, tags) {
        this._syncTags(tags);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
            }
        }, {
            tagsOnly: true
        });
    },
    _showTagsDefaultView: function() {
        this.getManageTagsCardBody().getLayout().setActiveItem('tagsHelpAndButtonsContainer');
    },

    // Add tags
    _onAddTags: function() {
        this.getManageTagsCardBody().getLayout().setActiveItem('addTagsPanel');
        this._scrollTagsIntoView();
    },
    _onAddTagsSave: function(win, tags) {
        this._syncTags(tags, true);
        this.manageStudentsController.notifyMultipleGroupsChange({
            scope: this,
            success: function() {
            }
        }, {
            tagsOnly: true
        });
    },


    // Clear tags
    _onClearTags: function() {
        this.getManageTagsCardBody().getLayout().setActiveItem('clearTagsPanel');
        this._scrollTagsIntoView();
    },

    _onClearTagsConfirmed: function() {
        Ext.Array.each(this.groupRecords, function(groupRecord) {
            groupRecord.set('tags', []);
        }, {
            tagsOnly: true
        }, this);
        this.manageStudentsController.notifyMultipleGroupsChange();
    },



    /************************************************
     *
     * Merge groups
     *
     ************************************************/

    _onMergeGroupsButton: function(button, pressed) {
        this.getMergeGroupsHelp().hide();
        this.getMergeGroupsButton().hide();
        var confirmContainer = this.getConfirmMergeGroupsContainer();
        confirmContainer.show();
        this._scrollIntroView(confirmContainer);
    },

    _showMergeGroupsDefaultView: function() {
        this.getConfirmMergeGroupsContainer().hide();
        this.getMergeGroupsHelp().show();
        this.getMergeGroupsButton().show();
    },
    _onMergeGroupsCancel: function() {
        this._showMergeGroupsDefaultView();
        this._scrollIntroView(this.getMergeGroups());
    },

    _onMergeGroupsConfirm: function() {
        var assignmentRecord = this.manageStudentsController.assignmentRecord;
        var record = Ext.create('devilry_subjectadmin.model.MergeIntoGroup');
        record.proxy.setUrl(assignmentRecord.get('id'));

        var targetRecord = this.groupRecords[0];
        var source_group_ids = [];
        for(var index=1; index<this.groupRecords.length; index++)  {
            var sourceRecord = this.groupRecords[index];
            source_group_ids.push({
                id: sourceRecord.get('id')
            });
        }

        record.set('source_group_ids', source_group_ids);
        record.set('target_group_id', targetRecord.get('id'));

        record.save({
            scope: this,
            callback: function(result, operation) {
                if(operation.success) {
                    this._onMergeGroupsSuccess(result);
                } else {
                    // NOTE: Errors are handled in _onMergeIntoGroupProxyError
                }
            }
        });
    },
    _onMergeIntoGroupProxyError: function(proxy, response, operation) {
        this.handleProxyUsingHtmlErrorDialog(response, operation);
    },
    _onMergeGroupsSuccess: function(result) {
        var target_group_id = result.get('target_group_id');
        this.manageStudentsController.reloadGroups([target_group_id]);
    },


    
    /************************************************
     * 
     * DELETE
     *
     ***********************************************/
    _onDelete: function() {
        this.manageStudentsController.removeGroups(this.groupRecords);
    }
});
