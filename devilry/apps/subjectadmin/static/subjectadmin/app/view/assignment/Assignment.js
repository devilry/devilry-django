/**
 * Assignment dashboard view (overview of an assignment).
 */
Ext.define('subjectadmin.view.assignment.Assignment' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.assignment',
    cls: 'assignment sidebarlayout',
    requires: [
        'themebase.layout.RightSidebar',
        'subjectadmin.view.ActionList'
    ],


    /**
     * @cfg {String} subject_shortname (required)
     */

    /**
     * @cfg {String} period_shortname (required)
     */

    /**
     * @cfg {String} assignment_shortname (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'rightsidebar',
            frame: false,

            //var currenturl = Ext.String.format('#{0}/{1}/{2}'

            items: [{
                xtype: 'container',
                cls: 'centercolumn',
                region: 'main',
                items: [{
                    xtype: 'container',
                    cls: 'centerbox',
                    items: [{
                        xtype: 'box',
                        html: Ext.String.format('<h2 class="centertitle">{0}</h2>', this.assignment_shortname),
                    }, {
                        xtype: 'actionlist',
                        cls: 'centerbody',
                        links: [{
                            url: '#/@@create-new-assignment/@@chooseperiod',
                            text: dtranslate('themebase.edit-something')
                        }, {
                            url: '#',
                            text: dtranslate('subjectadmin.assignment.browse-and-manage-students')
                        }, {
                            url: '#/@@register-for-final-exams',
                            text: dtranslate('subjectadmin.assignment.manage-deadlines')
                        }, {
                            url: '#/@@global-statistics',
                            buttonType: 'danger',
                            text: dtranslate('themebase.delete-something')
                        }]
                    }]
                }]
            }, {
                xtype: 'container',
                border: false,
                region: 'sidebar',
                items: [{
                    xtype: 'box',
                    html: 'Something'
                }]
            }]
        });
        this.callParent(arguments);
    }
});
