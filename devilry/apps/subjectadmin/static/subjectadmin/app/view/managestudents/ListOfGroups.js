/**
 * List of groups.
 */
Ext.define('subjectadmin.view.managestudents.ListOfGroups' ,{
    extend: 'Ext.grid.Panel',
    alias: 'widget.listofgroups',
    cls: 'listofgroups',
    store: 'Groups',
    hideHeaders: true,


    col1TemplateString: [
        '<div class="col1Wrapper">',
        '   <div class="name">{name}</div>',
        '   <div class="username">{username}</div>',
        '   <tpl if="hasFeedback">',
        '       <tpl if="feedback__is_passing_grade">',
        '           <div class="passinggrade">',
        '               <span class="passingstatus">{approvedText}</span>',
        '               <span class="grade">({feedback__grade})</span>',
        '           </div>',
        '       </tpl>',
        '       <tpl if="!feedback__is_passing_grade">',
        '           <div class="notpassinggrade">',
        '               <span class="passingstatus">{notApprovedText}</span>',
        '               <span class="grade">({feedback__grade})</span>',
        '           </div>',
        '       </tpl>',
        '   </tpl>',
        '</div>'
    ],
    col2TemplateString: [
        '<div class="col2Wrapper">',
        '   <tpl if="is_open">',
        '       <div class="open">{openText}</div>',
        '   </tpl>',
        '   <tpl if="!is_open">',
        '       <div class="closed">{closedText}</div>',
        '   </tpl>',
        '   <div class="deliveries">',
        '       <tpl if="deliveries == 1">{deliveries} {deliveryText}</tpl>',
        '       <tpl if="deliveries &gt; 1">{deliveries} {deliveriesText}</tpl>',
        '   <div>',
        '</div>'
    ],


    initComponent: function() {
        this.approvedText = dtranslate('themebase.approved');
        this.notApprovedText = dtranslate('themebase.notapproved');
        this.openText = dtranslate('themebase.open');
        this.closedText = dtranslate('themebase.closed');
        this.deliveriesText = dtranslate('themebase.deliveries');
        this.deliveryText = dtranslate('themebase.delivery');

        this.col1Template = Ext.create('Ext.XTemplate', this.col1TemplateString);
        this.col2Template = Ext.create('Ext.XTemplate', this.col2TemplateString);
        Ext.apply(this, {
            columns: [{
                header: 'Col1',  dataIndex: 'id', flex: 1,
                renderer: this.renderCol1
            }, {
                header: 'Col2',  dataIndex: 'id', width: 100,
                renderer: this.renderCol2
            }],
        });
        this.callParent(arguments);
    },

    renderCol1: function(unused, unused2, record) {
        return this.col1Template.apply(Ext.apply(record.data, {
            name: this.getNameDivContent(record),
            username: this.getUsernameDivContent(record),
            notApprovedText: this.notApprovedText,
            hasFeedback: record.get('feedback__save_timestamp') != null,
            approvedText: this.approvedText
        }));
    },

    renderCol2: function(unused, unused2, record) {
        return this.col2Template.apply({
            deliveries: 2,
            is_open: record.get('is_open'),
            openText: this.openText,
            closedText: this.closedText,
            deliveriesText: this.deliveriesText,
            deliveryText: this.deliveryText
        });
    },

    /** Get the text for the fullname DIV.
     *
     * Prioritized in this order:
     *
     * 1. If no students, use the ID
     * 2. Name of first student.
     * 3. Username of first student.
     *
     * This view is optimized for single student assignments.
     * */
    getNameDivContent: function(record) {
        var students = record.get('students');
        if(students.length == 0) {
            return record.get('id');
        }
        var firstStudent = students[0];
        if(firstStudent.student__devilryuserprofile__full_name) {
            return firstStudent.student__devilryuserprofile__full_name;
        }
        return firstStudent.student__username;
    },

    /**
     * Get the text for the username DIV.
     *
     * Prioritized in this order:
     * 1. If no students, translate "Group have no students"
     * 2. Username of first student.
     * */
    getUsernameDivContent: function(record) {
        var students = record.get('students');
        if(students.length == 0) {
            return dtranslate('subjectadmin.managestudents.group-have-no-students');
        }
        var firstStudent = students[0];
        return firstStudent.student__username;
    }
});
