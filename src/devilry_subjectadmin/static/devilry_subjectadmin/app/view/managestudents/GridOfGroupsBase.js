/**
 * Base class for grids of groups.
 */
Ext.define('devilry_subjectadmin.view.managestudents.GridOfGroupsBase' ,{
    extend: 'Ext.grid.Panel',
    border: 1,
    frame: true,

    groupInfoColTemplateString: [
        '<div class="groupInfoWrapper groupInfoWrapper_{id}" style="white-space:normal !important;">',
            '<div class="name"><strong>',
                '<tpl if="groupUrlPrefix">',
                    '<a href="{groupUrlPrefix}{id}">',
                        '{fullnames}',
                    '</a>',
                '<tpl else>',
                    '{fullnames}',
                '</tpl>',
            '</strong></div>',
            '<tpl if="groupname">',
                '<div class="groupname">{groupname}</div>',
            '</tpl>',
            '<div class="username"><small class="muted">{usernames}</small></div>',
            '<div class="status">',
                '<div class="status-{status}">',
                    '<tpl if="status === \'corrected\'">',
                        '<tpl if="feedback.is_passing_grade">',
                            '<div class="passinggrade">',
                                '<small class="passingstatus text-success">{approvedText}</small>',
                                ' <small class="grade text-success">({feedback.grade})</small>',
                            '</div>',
                        '</tpl>',
                        '<tpl if="!feedback.is_passing_grade">',
                            '<div class="notpassinggrade">',
                            '<small class="passingstatus text-warning">{notApprovedText}</small>',
                            ' <small class="grade text-warning">({feedback.grade})</small>',
                            '</div>',
                        '</tpl>',
                    '<tpl elseif="status === \'waiting-for-deliveries\'">',
                        '<em><small class="muted">', gettext('Waiting for deliveries'), '</small></em>',
                    '<tpl elseif="status === \'waiting-for-feedback\'">',
                        '<em><small class="muted">', gettext('Waiting for feedback'), '</small></em>',
                    '<tpl else>',
                        '<span class="label label-important">{status}</span>',
                    '</tpl>',
                '</div>',
            '</div>',
        '</div>'
    ],
    metadataColTemplateString: [
        '<div class="metadataWrapper">',
            //'<tpl if="is_open">',
                //'<div class="open"><small class="text-info">{openText}</small></div>',
            //'<tpl else>',
                //'<div class="closed"><small class="muted">{closedText}</small></div>',
            //'</tpl>',
            '<tpl if="num_deliveries != 0">',
                '<div style="padding-top: 15px;">',
                    '<span class="num_deliveries badge" title="{num_deliveries} {[this.getDeliveriesLabel(values.num_deliveries)]}">',
                        '{num_deliveries} {[this.ellipsis(this.getDeliveriesLabel(values.num_deliveries), 7)]}',
                    '</span>',
                '</div>',
            '</tpl>',
        '</div>', {
            getDeliveriesLabel: function(num_deliveries) {
                if(num_deliveries === 1) {
                    return gettext('delivery');
                } else {
                    return gettext('deliveries');
                }
            },
            ellipsis: function(s, max) {
                return Ext.String.ellipsis(s, max);
            }
        }
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
    tagsListTemplateString: [
        '<div class="tagsWrapper">',
            '<ul class="unstyled">',
            '<tpl for="tags">',
                '<li class="tag">',
                    '{tag}',
                '</li>',
            '</tpl>',
            '</ul>',
        '</div>'
    ],

    initComponent: function() {
        var cssclasses = 'devilry_subjectadmin_gridofgroupsbase bootstrap';
        if(this.cls) {
            cssclasses += ' ' + this.cls;
        }
        this.cls = cssclasses;
        this.setTemplateVariables();
        this.columns = this.getColumns();
        this.groupUrlPrefix = this.getGroupUrlPrefix();
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
            dataIndex: 'user',
            width: 75,
            menuDisabled: true,
            renderer: this.renderMetadataCol,
            sortable: false
        };
    },

    getExaminersColConfig: function() {
        this.examinersListTemplate = Ext.create('Ext.XTemplate', this.examinersListTemplateString);
        return {
            header: gettext('Examiners'),
            dataIndex: 'examiners',
            flex: 1,
            menuDisabled: true,
            renderer: this.renderExaminersCol,
            sortable: false
        };
    },

    getTagsColConfig: function() {
        this.tagsListTemplate = Ext.create('Ext.XTemplate', this.tagsListTemplateString);
        return {
            header: gettext('Tags'),
            dataIndex: 'tags',
            flex: 1,
            menuDisabled: true,
            renderer: this.renderTagsCol,
            sortable: false
        };
    },

    renderGroupMembersCol: function(unused, unused2, record) {
        var groupname = record.get('name');
        if(!Ext.isEmpty(groupname)) {
            groupname = Ext.String.ellipsis(groupname, 20);
        }
        var data = {
            fullnames: this.getFullnames(record),
            groupname: groupname,
            usernames: this.getUsernames(record),
            notApprovedText: this.notApprovedText,
            approvedText: this.approvedText,
            groupUrlPrefix: this.groupUrlPrefix
        };
        Ext.apply(data, record.data);
        return this.groupInfoColTemplate.apply(data);
    },

    renderMetadataCol: function(unused, unused2, record) {
        return this.metadataColTemplate.apply({
            num_deliveries: record.get('num_deliveries'),
            is_open: record.get('is_open'),
            openText: this.openText,
            closedText: this.closedText
        });
    },

    renderExaminersCol: function(unused, unused2, record) {
        return this.examinersListTemplate.apply({
            examiners: record.get('examiners')
        });
    },

    renderTagsCol: function(unused, unused2, record) {
        return this.tagsListTemplate.apply({
            tags: record.get('tags')
        });
    },

    /** Get the text for the fullname DIV.
     *
     * Prioritized in this order:
     *
     * 1. If no candidates, return "No-students(groupID=ID)"
     * 2. Comma separated list of full names, where the string "Missing-fullname(userID=ID)" is used when full name is missing
     * */
    getFullnames: function(record) {
        var candidates = record.get('candidates');
        if(candidates.length === 0) {
            return Ext.String.format('{0}(groupID={1})', gettext('No-students'), record.get('id'));
        }
        var names = [];
        for(var index=0; index<candidates.length; index++)  {
            var candidate = candidates[index];
            var full_name = candidate.user.full_name;
            if(Ext.isEmpty(full_name)) {
                full_name = Ext.String.format('{0}(userID={1})',
                    gettext('Missing-fullname'), candidate.user.id);
            }
            names.push(full_name);
        }
        return names.join('<br/>');
    },

    /**
     * Get the text for the username DIV.
     *
     * Prioritized in this order:
     * 1. If no candidates, return empty string.
     * 2. Comma-separated list of usernames.
     * */
    getUsernames: function(record) {
        var candidates = record.get('candidates');
        if(candidates.length === 0) {
            return '';
        }
        var usernames = [];
        for(var index=0; index<candidates.length; index++)  {
            var candidate = candidates[index];
            usernames.push(candidate.user.username);
        }
        return usernames.join(', ');
    },



    /**
     * Override this if you want the fullnames to be a link.
     */
    getGroupUrlPrefix: function() {
        return null;
    }
});
