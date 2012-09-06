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
        'devilry_subjectadmin.utils.UrlLookup'
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
        ref: 'deliveriesList',
        selector: 'viewport singlegroupview deliverieslist'
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
            'viewport singlegroupview deliverieslist': {
                delivery_link_clicked: this._onDeliveryLink
            },

            'viewport singlegroupview admingroupinfo_deadlinescontainer': {
                render: this._onRenderDeadlinesContainer
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
            multiselectHowto: this.manageStudentsController.getMultiSelectHowto(),
            multiselectWhy: this._getMultiSelectWhy(),
            studentsStore: this._createStudentsStore(),
            examinersStore: this._createExaminersStore(),
            tagsStore: this._createTagsStore(),
            assignment_id: this.manageStudentsController.assignmentRecord.get('id'),
            groupRecord: this.groupRecord
        });
    },

    _onRender: function() {
        //console.log('render SingleGroupSelectedView');
    },

    _getMultiSelectWhy: function() {
        return interpolate(gettext('Selecting multiple %(groups_term)s enables you to change %(examiners_term)s and %(tags_term)s on multiple %(groups_term)s, and merge multiple %(groups_term)s into a single %(group_term)s.'), {
            groups_term: gettext('groups'),
            examiners_term: gettext('examiners'),
            tags_term: gettext('tags'),
            group_term: gettext('group')
        }, true);
    },

    _confirm: function(config) {
        Ext.MessageBox.show({
            title: config.title,
            msg: config.msg,
            buttons: Ext.MessageBox.YESNO,
            icon: Ext.MessageBox.QUESTION,
            scope: this,
            fn: function(buttonid) {
                if(buttonid == 'yes') {
                    Ext.callback(config.callback, this);
                }
            }
        });
    },


    /*********************************************
     *
     * Metadata views
     *
     *********************************************/
    _selectDelivery: function(delivery_id) {
        this._hightlightSelectedDelivery(delivery_id);
        var group_id = this.groupRecord.get('id');
        var prefix = devilry_subjectadmin.utils.UrlLookup.manageGroupAndShowDeliveryPrefix(
            this.manageStudentsController.assignmentRecord.get('id'),
            group_id);
        var hash = Ext.String.format('{0}{1}', prefix, delivery_id);
        this.application.route.setHashWithoutEvent(hash);
    },

    _onActiveFeedbackLink: function() {
        var delivery_id = this.groupRecord.get('feedback').delivery_id;
        this._selectDelivery(delivery_id);
    },

    _onDeliveryLink: function(delivery_id) {
        this._selectDelivery(delivery_id);
    },




    /********************************************************
     *
     * AggregatedGroupInfo views (deadlines and deliveries)
     *
     ********************************************************/
    _onRenderDeadlinesContainer: function() {
        this.getDeadlinesContainer().setLoading(gettext('Loading') + ' ...');
        this.getDeliveriesList().setLoading(gettext('Loading') + ' ...');
        this.getAggregatedGroupInfoModel().load(this.groupRecord.get('id'), {
            scope: this,
            callback: function(aggregatedGroupInfoRecord, operation) {
                this.getDeadlinesContainer().setLoading(false);
                this.getDeliveriesList().setLoading(false);
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
        this.getDeliveriesList().populate(
            this.manageStudentsController.assignmentRecord.get('id'),
            this.groupRecord.get('id'),
            aggregatedGroupInfoRecord.get('deadlines'));

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
            deliveryPanel.el.scrollIntoView(this.getScrollableBody().body, false, true);
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
                // TODO: Notify the user about the change
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
    }
});
