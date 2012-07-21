/**
 * Base class for grids of groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.GridOfGroupsBase' ,{
    extend: 'Ext.grid.Panel',
    multiSelect: true,
    border: 1,
    frame: true,

    groupInfoColTemplateString: [
        '<div class="groupInfoWrapper">',
        '   <div class="name"><strong>{displayName}</strong></div>',
        '   <div class="username"><small>{displayUsername}</small></div>',
        '   <tpl if="hasFeedback">',
        '       <tpl if="feedback.is_passing_grade">',
        '           <div class="passinggrade">',
        '               <small class="passingstatus success">{approvedText}</small>',
        '               <small class="grade success">({feedback.grade})</small>',
        '           </div>',
        '       </tpl>',
        '       <tpl if="!feedback.is_passing_grade">',
        '           <div class="notpassinggrade">',
        '               <small class="passingstatus danger">{notApprovedText}</small>',
        '               <small class="grade danger">({feedback.grade})</small>',
        '           </div>',
        '       </tpl>',
        '   </tpl>',
        '</div>'
    ],
    metadataColTemplateString: [
        '<div class="metadataWrapper">',
        '   <tpl if="is_open">',
        '       <div class="open"><small class="success">{openText}</small></div>',
        '   </tpl>',
        '   <tpl if="!is_open">',
        '       <div class="closed"><small>{closedText}</small></div>',
        '   </tpl>',
        '   <tpl if="num_deliveries != 0">',
        '       <div class="num_deliveries countbox">',
        '           <tpl if="num_deliveries == 1">{num_deliveries} {deliveryText}</tpl>',
        '           <tpl if="num_deliveries &gt; 1">{num_deliveries} {deliveriesText}</tpl>',
        '       <div>',
        '   </tpl>',
        '</div>'
    ],
    examinersListTemplateString: [
        '<div class="examinersWrapper">',
            '<ul class="unstyled">',
            '<tpl for="examiners">',
                '<li class="examiner">',
                    '<tpl if="user.full_name">',
                        '{user.full_name}',
                    '<tpl else>',
                        '{user.username}',
                    '</tpl>',
                '</li>',
            '</tpl>',
            '</ul>',
        '</div>'
    ],

    initComponent: function() {
        var cssclasses = 'devilry_subjectadmin_gridofgroupsbase';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        this.setTemplateVariables();
        this.columns = this.getColumns();
        this.callParent(arguments);
    },

    getColumns: function() {
        throw "getColumns must be implemented in subclasses";
    },

    setTemplateVariables: function() {
        this.approvedText = pgettext('group', 'Passed');
        this.notApprovedText = pgettext('group', 'Failed');
        this.openText = pgettext('group', 'Open');
        this.closedText = pgettext('group', 'Closed');
        this.deliveriesText = gettext('Deliveries');
        this.deliveryText = gettext('Delivery');

    },

    getGroupInfoColConfig: function() {
        this.groupInfoColTemplate = Ext.create('Ext.XTemplate', this.groupInfoColTemplateString);
        return {
            header: gettext('Group info'),
            dataIndex: 'id',
            flex: 2,
            menuDisabled: true,
            renderer: this.renderGroupMembersCol,
            sortable: false
        };
    },

    getMetadataColConfig: function() {
        this.metadataColTemplate = Ext.create('Ext.XTemplate', this.metadataColTemplateString);
        return {
            header: gettext('Metadata'),
            dataIndex: 'id',
            width: 95,
            menuDisabled: true,
            renderer: this.renderMetadataCol,
            sortable: false
        };
    },

    getExaminersColConfig: function() {
        this.examinersListTemplate = Ext.create('Ext.XTemplate', this.examinersListTemplateString);
        return {
            header: gettext('Examiners'),
            dataIndex: 'id',
            flex: 1,
            menuDisabled: true,
            renderer: this.renderExaminersCol,
            sortable: false
        };
    },

    renderGroupMembersCol: function(unused, unused2, record) {
        var data = {
            displayName: this.getNameDivContent(record),
            displayUsername: this.getUsernameDivContent(record),
            notApprovedText: this.notApprovedText,
            hasFeedback: record.get('feedback') != null,
            approvedText: this.approvedText
        };
        Ext.apply(data, record.data);
        return this.groupInfoColTemplate.apply(data);
    },

    renderMetadataCol: function(unused, unused2, record) {
        return this.metadataColTemplate.apply({
            num_deliveries: record.get('num_deliveries'),
            is_open: record.get('is_open'),
            openText: this.openText,
            closedText: this.closedText,
            deliveriesText: this.deliveriesText,
            deliveryText: this.deliveryText
        });
    },

    renderExaminersCol: function(unused, unused2, record) {
        return this.examinersListTemplate.apply({
            examiners: record.get('examiners')
        });
    },

    /** Get the text for the fullname DIV.
     *
     * Prioritized in this order:
     *
     * 1. If no candidates, use the ID
     * 2. Name of first student.
     * 3. Username of first student.
     *
     * This view is optimized for single student assignments.
     * */
    getNameDivContent: function(record) {
        var candidates = record.get('candidates');
        if(candidates.length == 0) {
            return record.get('id');
        }
        var firstCandidate = candidates[0];
        if(firstCandidate.user.full_name) {
            return firstCandidate.user.full_name;
        }
        return firstCandidate.user.username;
    },

    /**
     * Get the text for the username DIV.
     *
     * Prioritized in this order:
     * 1. If no candidates, translate "Group have no candidates"
     * 2. Username of first student.
     * */
    getUsernameDivContent: function(record) {
        var candidates = record.get('candidates');
        if(candidates.length == 0) {
            return gettext('Group have no candidates');
        }
        var firstCandidate = candidates[0];
        return firstCandidate.user.username;
    }
});
