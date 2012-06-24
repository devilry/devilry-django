/**
 * Controller for the subject overview.
 */
Ext.define('devilry_subjectadmin.controller.subject.Overview', {
    extend: 'Ext.app.Controller',
    mixins: {
        'setBreadcrumb': 'devilry_subjectadmin.utils.BasenodeBreadcrumbMixin'
    },

    views: [
        'subject.Overview',
        'subject.ListOfPeriods',
        'ActionList'
    ],

    stores: ['Periods'],
    models: ['Subject'],

    refs: [{
        ref: 'globalAlertmessagelist',
        selector: 'subjectoverview>alertmessagelist'
    }, {
        ref: 'deleteButton',
        selector: 'subjectoverview #deleteButton'
    }, {
        ref: 'renameButton',
        selector: 'subjectoverview #renameButton'
    }, {
        ref: 'actions',
        selector: 'subjectoverview #actions'
    }, {
        ref: 'subjectOverview',
        selector: 'subjectoverview'
    }, {
        ref: 'adminsBox',
        selector: 'subjectoverview #admins'
    }],

    init: function() {
        this.control({
            'viewport subjectoverview': {
                render: this._onSubjectViewRender
            },
            'viewport subjectoverview editablesidebarbox[itemId=gradeeditor] button': {
                click: this._onEditGradeEditor
            },
            'viewport subjectoverview #deleteButton': {
                click: this._onNotImplemented
            },
            'viewport subjectoverview #renameButton': {
                click: this._onNotImplemented
            }
        });
    },

    _onNotImplemented: function() {
        Ext.MessageBox.alert('Unavailable', 'Not implemented yet');
    },

    _onSubjectViewRender: function() {
        this.setLoadingBreadcrumb();
        this.subject_id = this.getSubjectOverview().subject_id;
        this._loadSubject(this.subject_id);
        this._loadPeriods();
    },

    _initAdmins: function() {
        this.getAdminsBox().updateBody([
            gettext('On this subject:'),
            '<ul class="devilry_administratorlist">',
                '<tpl for="admins">',
                    '<li>',
                        '<a href="mailto:{email}">',
                            '<tpl if="full_name != null">',
                                '{full_name}',
                            '</tpl>',
                            '<tpl if="full_name == null">',
                                '{username}',
                            '</tpl>',
                        '</a>',
                    '</li>',
                '</tpl>',
            '</ul>',
            gettext('Inherited:'),
            '<ul class="devilry_inherited_administratorlist">',
                '<tpl for="inherited_admins">',
                    '<li>',
                        '<a href="mailto:{user.email}">',
                            '<tpl if="user.full_name != null">',
                                '{user.full_name}',
                            '</tpl>',
                            '<tpl if="user.full_name == null">',
                                '{user.username}',
                            '</tpl>',
                        '</a>',
                        ' ({basenode.path})',
                    '</li>',
                '</tpl>',
            '</ul>'
        ], {
            admins: this.subjectRecord.get('admins'),
            inherited_admins: this.subjectRecord.get('inherited_admins')
        });
    },

    _setMenuLabels: function() {
        var deleteLabel = Ext.create('Ext.XTemplate', gettext('Delete {something}')).apply({
            something: this.subjectRecord.get('short_name')
        });
        var renameLabel = Ext.create('Ext.XTemplate', gettext('Rename {something}')).apply({
            something: this.subjectRecord.get('short_name')
        });
        this.getDeleteButton().setText(deleteLabel);
        this.getRenameButton().setText(renameLabel);
    },

    _loadPeriods: function() {
        this.getPeriodsStore().loadPeriodsInSubject(this.subject_id, this._onLoadPeriods, this);
    },

    _onLoadPeriods: function(records, operation) {
        if(operation.success) {
            
        } else {
            var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
            error.addErrors(operation);
            this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
        }
    },


    /** Implement methods required by LoadSubjectMixin */
    _loadSubject: function(subject_id) {
        this.getSubjectModel().load(subject_id, {
            scope: this,
            callback: function(record, operation) {
                if(operation.success) {
                    this._onLoadSubjectSuccess(record);
                } else {
                    this._onLoadSubjectFailure(operation);
                }
            }
        });
    },
    _onLoadSubjectSuccess: function(record) {
        this.subjectRecord = record;
        this.getActions().setTitle(record.get('long_name'));
        this.setBreadcrumb(this.subjectRecord);
        this._initAdmins();
        this._setMenuLabels();
    },
    _onLoadSubjectFailure: function(operation) {
        var error = Ext.create('devilry_extjsextras.RestfulApiProxyErrorHandler', operation);
        error.addErrors(operation);
        this.getGlobalAlertmessagelist().addMany(error.errormessages, 'error');
    }
});
