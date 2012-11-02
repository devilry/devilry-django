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

    views: [
        'managestudents.SingleGroupSelectedView',
        'managestudents.SelectExaminersGrid'
    ],

    refs: [{
        ref: 'scrollableBody',
        selector: 'viewport singlegroupview'
    }, {
        ref: 'deadlinesContainer',
        selector: 'viewport singlegroupview admingroupinfo_deadlinescontainer'
    }, {
        ref: 'examinerRoleList',
        selector: 'viewport singlegroupview #examinerRoleList'

    }, {

    // Students
        ref: 'studentsCardBody',
        selector: 'viewport singlegroupview managestudentsonsingle #cardBody'
    }, {

    // Examiners
        ref: 'examinersCardBody',
        selector: 'viewport singlegroupview manageexaminersonsingle #cardBody'
    }, {
        ref: 'setExaminersGrid',
        selector: 'viewport singlegroupview manageexaminersonsingle #setExaminersPanel selectexaminersgrid'
    }, {

    // Tags
        ref: 'tagsCardBody',
        selector: 'viewport singlegroupview managetagsonsingle #cardBody'
    }],

    init: function() {
        this.application.addListener({
            scope: this,
            managestudentsSingleGroupSelected: this._onSingleGroupSelected
        });
        this.control({
            'viewport singlegroupview': {
                render: this._onRender
            },

            'viewport singlegroupview singlegroupmetainfo': {
                active_feedback_link_clicked: this._onActiveFeedbackLink
            },

            'viewport singlegroupview admingroupinfo_deadlinescontainer': {
                render: this._onRenderDeadlinesContainer
            },
            'viewport singlegroupview admingroupinfo_delivery #feedback': {
                render: this._onFeedbackRender
            },

            'viewport singlegroupview #examinerRoleList': {
                render: this._onExaminerRoleListRender
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

    _onSingleGroupSelected: function(manageStudentsController, groupRecord) {
        this.manageStudentsController = manageStudentsController;
        this.groupRecord = groupRecord;
        this._refreshBody();
    },

    _refreshBody: function() {
        this.manageStudentsController.setBody({
            xtype: 'singlegroupview',
            studentsStore: this._createStudentsStore(),
            examinersStore: this._createExaminersStore(),
            tagsStore: this._createTagsStore(),
            assignment_id: this.manageStudentsController.assignmentRecord.get('id'),
            groupRecord: this.groupRecord,
            period_id: this.manageStudentsController.assignmentRecord.get('parentnode')
        });
    },

    _onRender: function() {
        //console.log('render SingleGroupSelectedView');
    },

    _onExaminerRoleListRender: function() {
        devilry_authenticateduserinfo.UserInfo.load(function(authenticatedUser) {
            var isExaminer = Ext.Array.some(this.groupRecord.get('examiners'), function(examiner) {
                if(examiner.user.id === authenticatedUser.get('id')) {
                    return true;
                }
            }, this);
            this.getExaminerRoleList().removeAll();
            this.getExaminerRoleList().add({
                type: 'info',
                messagetpl: [
                    '<div class="pull-left" style="margin-right: 20px;">',
                        '<h4 style="margin-bottom: 2px;">',
                            gettext('Add feedback?'),
                        '</h4>',
                        '<tpl if="isExaminer">',
                            ' <a href="{examinerui_url}" target="_blank" class="btn btn-small btn-inverse">',
                                gettext('Examiner interface'),
                                ' <i class="icon-share-alt icon-white"></i>',
                            '</a>',
                        '<tpl else>',
                            ' <a href="{make_examiner}" class="btn btn-small btn-inverse make_me_examiner">',
                                gettext('Make me examiner'),
                            '</a>',
                        '</tpl>',
                    '</div>',
                    '<tpl if="isExaminer">',
                        gettext('You are examiner on this group, which means you can provide feedback yourself.'),
                    '<tpl else>',
                        gettext('You are not examiner on this group, which means you can not provide feedback yourself.'),
                    '</tpl>',
                    '<div class="clearfix"></div>'
                ],
                messagedata: {
                    isExaminer: isExaminer,
                    examinerui_url: devilry_subjectadmin.utils.UrlLookup.examinerGroupOverview(this.groupRecord.get('id'))
                },
                listeners: {
                    scope: this,
                    element: 'el',
                    delegate: '.make_me_examiner',
                    click: function(e) {
                        e.preventDefault();
                        this._onMakeMeExaminer();
                    }
                }
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
    _onRenderDeadlinesContainer: function() {
        this.getDeadlinesContainer().setLoading(gettext('Loading') + ' ...');
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
        this.getDeadlinesContainer().populate(aggregatedGroupInfoRecord, active_feedback);

        var delivery_id = this.manageStudentsController.getOverview().select_delivery_on_load;
        this.manageStudentsController.getOverview().select_delivery_on_load = undefined; //NOTE: We only want to get it on the first load.
        if(!Ext.isEmpty(delivery_id)) {
            this._hightlightSelectedDelivery(delivery_id);
        }
    },
    _onAggregatedGroupInfoLoadFailure: function(operation) {
        console.log('AggregatedGroupInfo load error', operation); // TODO: Handle load errors
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
            alert(Ext.String.format('Invalid delivery: {0}'), delivery_id);
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

    _createStudentsStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getCandidateModel(),
            data: this.groupRecord.get('candidates')
        });
        return store;
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

    _createExaminersStore: function() {
        var store = Ext.create('Ext.data.Store', {
            model: this.getExaminerModel(),
            data: this.groupRecord.get('examiners')
        });
        return store;
    },
    _onSetExaminers: function() {
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
            console.log('user', authenticatedUser.data);
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

    _createTagsStore: function() {
        //console.log(this.groupRecord.data);
        var store = Ext.create('Ext.data.Store', {
            model: this.getTagModel(),
            data: this.groupRecord.get('tags')
        });
        return store;
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
                // TODO: Notify the user about the change
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
