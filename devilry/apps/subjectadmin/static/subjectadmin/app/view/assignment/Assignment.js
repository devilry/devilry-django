/**
 * Assignment dashboard view (overview of an assignment).
 */
Ext.define('subjectadmin.view.assignment.Assignment' ,{
    extend: 'Ext.container.Container',
    alias: 'widget.assignment',
    cls: 'assignment sidebarlayout',
    requires: [
        'themebase.layout.RightSidebar',
        'themebase.CenterTitle',
        'themebase.EditableSidebarBox',
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

            items: [{
                xtype: 'container',
                cls: 'centercolumn',
                region: 'main',
                items: [{
                    xtype: 'container',
                    cls: 'centerbox',
                    items: [{
                        xtype: 'centertitle',
                        title: this.assignment_shortname,
                    }, {
                        xtype: 'actionlist',
                        cls: 'centerbody',
                        links: [{
                            url: '#',
                            text: dtranslate('themebase.edit-something')
                        }, {
                            url: '#',
                            text: dtranslate('subjectadmin.assignment.manage-students')
                        }, {
                            url: '#',
                            text: dtranslate('subjectadmin.assignment.manage-deadlines')
                        }, {
                            url: '#',
                            buttonType: 'danger',
                            text: dtranslate('themebase.delete-something')
                        }]
                    }]
                }, {
                    xtype: 'container',
                    cls: 'twocol-centerbox',
                    layout: 'column',
                    items: [{
                        xtype: 'container',
                        cls: 'centerbox',
                        columnWidth: .5,
                        items: [{
                            xtype: 'centertitle',
                            title: Ext.String.ellipsis(dtranslate('subjectadmin.assignment.waitingforfeedback'), 25)
                        }, {
                            xtype: 'box',
                            cls: 'centerbody',
                            html: 'TODO'
                        }]
                    }, {
                        xtype: 'container',
                        columnWidth: .5,
                        cls: 'centerbox',
                        items: [{
                            xtype: 'centertitle',
                            title: Ext.String.ellipsis(dtranslate('subjectadmin.assignment.upcoming-deadlines'), 25)
                        }, {
                            xtype: 'box',
                            cls: 'centerbody',
                            html: 'TODO'
                        }]
                    }]
                }]
            }, {
                xtype: 'container',
                border: false,
                region: 'sidebar',
                items: [{
                    xtype: 'editablesidebarbox',
                    itemId: 'gradeeditor',
                    title: dtranslate('subjectadmin.assignment.gradeeditor')
                }, {
                    xtype: 'editablesidebarbox',
                    itemId: 'publishingtime',
                    title: dtranslate('themebase.loading'),
                    data: {text: ''}
                }]
            }]
        });
        this.callParent(arguments);
    }
});
