/**
 * List of groups.
 */
Ext.define('subjectadmin.view.managestudents.ListOfGroups' ,{
    extend: 'Ext.grid.Panel',
    alias: 'widget.listofgroups',
    cls: 'listofgroups',
    store: 'Groups',
    hideHeaders: true,
    multiSelect: true,

    col1TemplateString: [
        '<div class="col1Wrapper">',
        '   <div class="name"><strong>{displayName}</strong></div>',
        '   <div class="username"><small>{displayUsername}</small></div>',
        '   <tpl if="hasFeedback">',
        '       <tpl if="feedback__is_passing_grade">',
        '           <div class="passinggrade">',
        '               <small class="passingstatus success">{approvedText}</small>',
        '               <small class="grade success">({feedback__grade})</small>',
        '           </div>',
        '       </tpl>',
        '       <tpl if="!feedback__is_passing_grade">',
        '           <div class="notpassinggrade">',
        '               <small class="passingstatus danger">{notApprovedText}</small>',
        '               <small class="grade danger">({feedback__grade})</small>',
        '           </div>',
        '       </tpl>',
        '   </tpl>',
        '</div>'
    ],
    col2TemplateString: [
        '<div class="col2Wrapper smallerfont">',
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


    initComponent: function() {
        this.approvedText = dtranslate('themebase.passing_grade');
        this.notApprovedText = dtranslate('themebase.not_passing_grade');
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
        var data = {
            displayName: this.getNameDivContent(record),
            displayUsername: this.getUsernameDivContent(record),
            notApprovedText: this.notApprovedText,
            hasFeedback: record.get('feedback__save_timestamp') != null,
            approvedText: this.approvedText
        };
        Ext.apply(data, record.data);
        return this.col1Template.apply(data);
    },

    renderCol2: function(unused, unused2, record) {
        return this.col2Template.apply({
            num_deliveries: record.get('num_deliveries'),
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
