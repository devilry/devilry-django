/**
 * Plugin for {@link devilry_subjectadmin.controller.managestudents.Overview} that
 * adds the ability to show information about and edit a single group when
 * it is selected.
 */
Ext.define('devilry_subjectadmin.controller.managestudents.SingleGroupSelectedViewPlugin', {
    extend: 'Ext.app.Controller',

    mixins: [
        'devilry_subjectadmin.utils.DjangoRestframeworkProxyErrorMixin'
    ],

    requires: [
        'devilry_extjsextras.AlertMessage',
        'devilry_subjectadmin.view.managestudents.DeadlinesContainer',
        'Ext.fx.Animator',
        'devilry_subjectadmin.utils.UrlLookup',
        'devilry_authenticateduserinfo.UserInfo'
    ],

    models: [
        'Candidate',
        'Examiner',
        'Tag',
        'PopFromGroup',
        'AggregatedGroupInfo'
    ],

    stores: [
        'SingleGroupCandidates',
        'SingleGroupExaminers',
        'SingleGroupTags'
    ],

    views: [
        'managestudents.SingleGroupSelectedView',
        'managestudents.SelectExaminersGrid'
    ],

    refs: [{
        ref: 'scrollableBody',
        selector: 'viewport singlegroupview'
    }, {
        ref: 'singlegroupmetainfo',
        selector: 'viewport singlegroupview singlegroupmetainfo'

    }, {

    // Students
        ref: 'studentsBox',
        selector: 'viewport singlegroupview managestudentsonsingle'
    }, {
        ref: 'studentsCardBody',
        selector: 'viewport singlegroupview managestudentsonsingle #cardBody'
    }, {
        ref: 'studentsGrid',
        selector: 'viewport singlegroupview managestudentsonsingle studentsingroupgrid'
    }, {

    // Examiners
        ref: 'examinersBox',
        selector: 'viewport singlegroupview manageexaminersonsingle'
    }, {
        ref: 'examinersCardBody',
        selector: 'viewport singlegroupview manageexaminersonsingle #cardBody'
    }, {
        ref: 'setExaminersGrid',
        selector: 'viewport singlegroupview manageexaminersonsingle #setExaminersPanel selectexaminersgrid'
    }, {

    // Tags
        ref: 'tagsBox',
        selector: 'viewport singlegroupview managetagsonsingle'
    }, {
        ref: 'tagsCardBody',
        selector: 'viewport singlegroupview managetagsonsingle #cardBody'
    }, {
        ref: 'choosetagspanel',
        selector: 'viewport singlegroupview managetagsonsingle choosetagspanel'

    // Examiner role box
    }, {
        ref: 'examinerRoleBox',
        selector: 'viewport singlegroupview #examinerRoleBox'

    // Deadlines and deliveries
    }, {
        ref: 'deadlinesContainer',
        selector: 'viewport singlegroupview admingroupinfo_deadlinescontainer'

    // Dangerous actions
    }, {
        ref: 'dangerousactions',
        selector: 'viewport singlegroupview dangerousactions'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSingleGroupSelected: this._onSingleGroupSelected
        });
        this.delayedLoadTask = new Ext.util.DelayedTask(this._delayedLoad, this);

        this.control({
            'viewport singlegroupview': {
                render: this._onRender,
                make_me_examiner: this._onMakeMeExaminer
            },

            'viewport singlegroupview singlegroupmetainfo': {
                active_feedback_link_clicked: this._onActiveFeedbackLink
            },

            // Students
            'viewport singlegroupview managestudentsonsingle studentsingroupgrid': {
                popStudent: this._onPopStudent
            },
            'viewport singlegroupview managestudentsonsingle okcancelpanel#confirmPop': {
                cancel: this._showStudentsDefaultView,
                ok: this._onPopStudentConfirmed
            },

            // Examiners
            'viewport singlegroupview manageexaminersonsingle': {
                edit_examiners: this._onSetExaminers
            },
            'viewport singlegroupview manageexaminersonsingle okcancelpanel#setExaminersPanel': {
                cancel: this._showExaminersDefaultView,
                ok: this._onSetExaminersConfirmed
            },

            // Tags
            'viewport singlegroupview managetagsonsingle': {
                edit_tags: this._onSetTags
            },
            'viewport singlegroupview managetagsonsingle choosetagspanel#setTagsPanel': {
                cancel: this._showTagsDefaultView,
                savetags: this._onSetTagsConfirmed
            },

            // Deadlines
            'viewport singlegroupview admingroupinfo_delivery #feedback': {
                render: this._onFeedbackRender
            },

            // Delete
            'viewport singlegroupview #deleteButton': {
                click: this._onDelete
            }
        });
        this.mon(this.getPopFromGroupModel().proxy, {
            scope: this,
            exception: this._onPopFromGroupProxyError
        });
    },

    _getLowPriComponents: function() {
        return [
            this.getExaminersBox(),
            this.getTagsBox(),
            this.getDeadlinesContainer(),
            this.getExaminerRoleBox()
        ];
    },
    _getHighPriComponents: function() {
        return [
            this.getSinglegroupmetainfo(),
            this.getStudentsBox()
        ];
    },

    _onSingleGroupSelected: function(manageStudentsController, groupRecord) {
        this.delayedLoadTask.cancel();
        this.manageStudentsController = manageStudentsController;
        this.groupRecord = groupRecord;

        // Fade out all components, and set load mask
        Ext.Array.each(this._getLowPriComponents(), function(component) {
            this._fadeOut(component);
        }, this);
        Ext.Array.each(this._getHighPriComponents(), function(component) {
            this._fadeOut(component);
        }, this);
        this.getExaminerRoleBox().setLoading({
            msg: gettext('Loading detailed group information ...'),
            maskCls: 'devilry-white-mask'
        });

        // Load the most important stuff immediately
        this._closeAllEditors();
        this.manageStudentsController.setBodyCard('singlegroupSelected');
        this.getSinglegroupmetainfo().setGroupRecord(this.groupRecord);
        Ext.Array.each(this._getHighPriComponents(), function(component) {
            this._fadeIn(component);
        }, this);

        this._loadStudentsIntoStore();

        // Delayed loading of the less imporant stuff
        this.delayedLoadTask.delay(500);
    },

    _delayedLoad: function() {
        this._loadExaminersIntoStore();
        this._loadTagsIntoStore();
        this._setupExaminerLinkBox();
        Ext.Array.each(this._getLowPriComponents(), function(component) {
            this._fadeIn(component);
        }, this);
        this._populateDeadlinesContainer();
        this.getExaminerRoleBox().setLoading(false);
    },


    _fadeOut: function(component) {
//        component.getEl().setOpacity(0);
        component.getEl().animate({
            duration: 100,
            from: {opacity: 1.0},
            to: {opacity: 0}
        });
    },

    _fadeIn: function(component) {
        component.getEl().animate({
            duration: 200,
            from: {opacity: 0},
            to: {opacity: 1.0}
        });
    },

    _closeAllEditors: function() {
        this._showExaminersDefaultView();
        this._showStudentsDefaultView();
        this._showTagsDefaultView();
    },


    _onRender: function() {
        //console.log('render SingleGroupSelectedView');
    },

    _setupExaminerLinkBox: function() {
        devilry_authenticateduserinfo.UserInfo.load(function(authenticatedUser) {
            var isExaminer = Ext.Array.some(this.groupRecord.get('examiners'), function(examiner) {
                if(examiner.user.id === authenticatedUser.get('id')) {
                    return true;
                }
            }, this);
            var assignmentRecord = this.manageStudentsController.assignmentRecord;
            var examiner_url;
            if(assignmentRecord.get('delivery_types') === 0) {
                examiner_url = devilry_subjectadmin.utils.UrlLookup.examinerGroupOverview(this.groupRecord.get('id'));
            } else {
                examiner_url = devilry_subjectadmin.utils.UrlLookup.examinerGroupsOverviewStudents(assignmentRecord.get('id'));
            }
            this.getExaminerRoleBox().updateData({
                loading: false,
                isExaminer: isExaminer,
                is_published: assignmentRecord.get('is_published'),
                pubtimeOffset: assignmentRecord.formatPublishOffsetFromNow(),
                examinerui_url: examiner_url
            });
        }, this);
    },



    /*********************************************
     *
     * Metadata views
     *
     *********************************************/
    _selectDelivery: function(delivery_id) {
        var group_id = this.groupRecord.get('id');
        var prefix = devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
            this.manageStudentsController.assignmentRecord.get('id'),
            group_id);
        var hash = Ext.String.format('{0}{1}', prefix, delivery_id);
        this.application.route.setHashWithoutEvent(hash);
        window.location.reload(); // NOTE: Horrible hack to work around issues with autoscrolling in _hightlightSelectedDelivery
        //this._hightlightSelectedDelivery(delivery_id);
    },

    _onActiveFeedbackLink: function() {
        var delivery_id = this.groupRecord.get('feedback').delivery_id;
        this._selectDelivery(delivery_id);
    },

    _onFeedbackRender: function(component) {
        if(window.DevilrySettings.DEVILRY_ENABLE_MATHJAX) {
            MathJax.Hub.Queue(["Typeset", MathJax.Hub, component.el.id]);
        }
    },




    /********************************************************
     *
     * AggregatedGroupInfo views (deadlines and deliveries)
     *
     ********************************************************/
    _populateDeadlinesContainer: function() {
        this.getDeadlinesContainer().setLoading(gettext('Loading') + ' ...');
        this.getDeadlinesContainer().removeAll();
        this.getAggregatedGroupInfoModel().load(this.groupRecord.get('id'), {
            scope: this,
            callback: function(aggregatedGroupInfoRecord, operation) {
                this.getDeadlinesContainer().setLoading(false);
                if(operation.success) {
                    this._onAggregatedGroupInfoLoadSuccess(aggregatedGroupInfoRecord);
                } else {
                    this._onAggregatedGroupInfoLoadFailure(operation);
                }
            }
        });
    },
    _onAggregatedGroupInfoLoadSuccess: function(aggregatedGroupInfoRecord) {
        var active_feedback = this.groupRecord.get('feedback');
        var assignmentRecord = this.manageStudentsController.assignmentRecord;
        var delivery_types = assignmentRecord.get('delivery_types');
        this.getDeadlinesContainer().populate(aggregatedGroupInfoRecord, active_feedback, delivery_types);

        var delivery_id = this.manageStudentsController.getOverview().select_delivery_on_load;
        this.manageStudentsController.getOverview().select_delivery_on_load = undefined; //NOTE: We only want to get it on the first load.
        if(!Ext.isEmpty(delivery_id)) {
            this._hightlightSelectedDelivery(delivery_id);
        }
    },
    _onAggregatedGroupInfoLoadFailure: function(operation) {
        this.application.getAlertmessagelist().add({
            type: 'error',
            autoclose: false,
            message: gettext('An error occurred while loading detailed group information.')
        });
    },

    _hightlightSelectedDelivery: function(delivery_id) {
        var itemid = Ext.String.format('#delivery-{0}', delivery_id);
        var deliveryPanel = this.getDeadlinesContainer().down(itemid);
        if(deliveryPanel) {
            var container = deliveryPanel.up('admingroupinfo_deadline');
            container.expand();
            deliveryPanel.getEl().scrollIntoView(this.getScrollableBody().body, false, true);
            Ext.create('Ext.fx.Animator', {
                target: deliveryPanel.body,
                duration: 3000,
                keyframes: {
                    0: {
                        backgroundColor: '#FFFFFF'
                    },
                    20: {
                        backgroundColor: '#FBEED5'
                    },
                    50: {
                        backgroundColor: '#FBEED5'
                    },
                    100: {
                        backgroundColor: '#FFFFFF'
                    }
                }
            });
        } else {
            this.application.getAlertmessagelist().add({
                type: 'error',
                messagetpl: gettext('Invalid delivery ID: {id}.'),
                messagedata: {
                    id: delivery_id
                }
            });
        }
    },



    /************************************************
     *
     * Students
     *
     ***********************************************/
    _showStudentsDefaultView: function() {
        this.getStudentsCardBody().getLayout().setActiveItem('helpAndButtonsContainer');
    },

    _loadStudentsIntoStore: function() {
        this.getSingleGroupCandidatesStore().loadData(this.groupRecord.get('candidates'));
        if(this.groupRecord.get('candidates').length < 2) {
            this.getStudentsGrid().hideDeleteColumn();
        } else {
            this.getStudentsGrid().showDeleteColumn();
        }
    },

    _onPopStudent: function(candidateRecord) {
        this.getStudentsCardBody().getLayout().setActiveItem('confirmPop');
        var confirmPanel = this.getStudentsCardBody().down('#confirmPop');
        confirmPanel.candidateRecord = candidateRecord; // NOTE: temporary storage - removed in _onPopStudentConfirmed()
    },
    _onPopStudentConfirmed: function() {
        var confirmPanel = this.getStudentsCardBody().down('#confirmPop');
        var candidateRecord = confirmPanel.candidateRecord;
        confirmPanel.candidateRecord = undefined;

        var assignmentRecord = this.manageStudentsController.assignmentRecord;
        var record = Ext.create('devilry_subjectadmin.model.PopFromGroup');
        record.proxy.setUrl(assignmentRecord.get('id'));
        record.set('group_id', this.groupRecord.get('id'));
        record.set('candidate_id', candidateRecord.get('id'));
        record.save({
            scope: this,
            callback: function(result, operation) {
                if(operation.success) {
                    this._onPopStudentSuccess(result);
                } else {
                    // NOTE: Errors are handled in _onPopFromGroupProxyError
                }
            }
        });
    },

    _onPopStudentSuccess: function(result) {
        var group_id = result.get('group_id');
        var new_group_id = result.get('new_group_id');
        this.manageStudentsController.reloadGroups([group_id, new_group_id]);
    },
    _onPopFromGroupProxyError: function(proxy, response, operation) {
        this.handleProxyUsingHtmlErrorDialog(response, operation);
    },



    /************************************************
     *
     * Examiners
     *
     ***********************************************/
    _showExaminersDefaultView: function() {
        this.getExaminersCardBody().getLayout().setActiveItem('helpAndButtonsContainer');
    },

    _loadExaminersIntoStore: function() {
        this.getSingleGroupExaminersStore().loadData(this.groupRecord.get('examiners'));
    },
    _onSetExaminers: function() {
        this.getExaminersBox().setPeriodId(this.manageStudentsController.assignmentRecord.get('parentnode'));
        this.getExaminersCardBody().getLayout().setActiveItem('setExaminersPanel');
        var userIds = [];
        Ext.Array.each(this.groupRecord.get('examiners'), function(examiner) {
            userIds.push(examiner.user.id);
        }, this);
        var grid = this.getSetExaminersGrid();
        grid.selectUsersById(userIds);
    },

    _em: function(s) {
        return Ext.String.format('<em>{0}</em>', s);
    },
    _getDisplaynamesFromUserStore: function(userStore) {
        var displaynames = [];
        userStore.each(function(userRecord) {
            displaynames.push(this._em(userRecord.getDisplayName()));
        }, this);
        return displaynames;
    },

    _onSetExaminersConfirmed: function() {
        var grid = this.getSetExaminersGrid();
        var userStore = grid.getSelectedAsUserStore();
        devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeExaminers({
            groupRecord: this.groupRecord,
            userRecords: userStore.data.items,
            doNotDeleteUsers: false
        });
        this.manageStudentsController.notifySingleGroupChange({
            scope: this,
            success: function() {
                this.application.getAlertmessagelist().add({
                    type: 'success',
                    autoclose: true,
                    messagetpl: gettext('Changed examiners of {group} to: {examiners}.'),
                    messagedata: {
                        group: this._em(this.groupRecord.getIdentString()),
                        examiners: this._getDisplaynamesFromUserStore(userStore).join(', ')
                    }
                });
            }
        });
    },

    _onMakeMeExaminer: function() {
        devilry_authenticateduserinfo.UserInfo.load(function(authenticatedUser) {
            devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeExaminers({
                groupRecord: this.groupRecord,
                userRecords: [authenticatedUser],
                doNotDeleteUsers: true // Add instead of replace
            });
        }, this);
        this.manageStudentsController.notifySingleGroupChange({
            scope: this,
            success: function() {
                this.application.getAlertmessagelist().add({
                    type: 'success',
                    autoclose: true,
                    messagetpl: gettext('Added you as examiner for {group}.'),
                    messagedata: {
                        group: this._em(this.groupRecord.getIdentString())
                    }
                });
            }
        });
    },


    /***********************************************
     *
     * Tags
     *
     **********************************************/
    _showTagsDefaultView: function() {
        this.getTagsCardBody().getLayout().setActiveItem('helpAndButtonsContainer');
    },

    _loadTagsIntoStore: function() {
        this.getSingleGroupTagsStore().loadData(this.groupRecord.get('tags'));
        var tags = [];
        Ext.Array.each(this.groupRecord.get('tags'), function(tagobj) {
            tags.push(tagobj.tag);
        }, this);
        if(typeof this.getChoosetagspanel() !== 'undefined') {
            this.getChoosetagspanel().setInitialValue(tags.join(','));
        }
    },

    // Add tags

    _onSetTags: function() {
        this.getTagsCardBody().getLayout().setActiveItem('setTagsPanel');
    },
    _onSetTagsConfirmed: function(panel, tags) {
        devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup.mergeTags({
            groupRecord: this.groupRecord,
            sourceTags: tags,
            doNotDeleteTags: false
        });
        this.manageStudentsController.notifySingleGroupChange({
            scope: this,
            success: function() {
                this.application.getAlertmessagelist().add({
                    type: 'success',
                    autoclose: true,
                    messagetpl: gettext('Saved the following tags for {group}: {tags}'),
                    messagedata: {
                        group: this._em(this.groupRecord.getIdentString()),
                        tags: tags.length>0? tags.join(', '): this._em(gettext('No tags'))
                    }
                });
            }
        });
    },


    /************************************************
     * 
     * DELETE
     *
     ***********************************************/
    _onDelete: function() {
        this.manageStudentsController.removeGroups([this.groupRecord]);
    }
});
