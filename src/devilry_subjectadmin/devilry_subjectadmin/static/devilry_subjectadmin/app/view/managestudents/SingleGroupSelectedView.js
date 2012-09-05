/**
 * A panel that displays information about a single group.
 */
Ext.define('devilry_subjectadmin.view.managestudents.SingleGroupSelectedView' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.singlegroupview',
    cls: 'devilry_subjectadmin_singlegroupview',
    autoScroll: true,
    border: 0,
    bodyPadding: 20,

    requires: [
        'devilry_subjectadmin.view.managestudents.ManageStudentsOnSingle',
        'devilry_subjectadmin.view.managestudents.ManageExaminersOnSingle',
        'devilry_subjectadmin.view.managestudents.ManageTagsOnSingle',
        'devilry_subjectadmin.view.managestudents.SingleMetaInfo'
    ],

    /**
     * @cfg {string} multiselectHowto (required)
     */

    /**
     * @cfg {devilry_subjectadmin.model.Group} groupRecord (required)
     */

    /**
     * @cfg {Ext.data.Store} studentsStore (required)
     */

    /**
     * @cfg {Ext.data.Store} examinersStore (required)
     */

    /**
     * @cfg {Ext.data.Store} tagsStore (required)
     */


    initComponent: function() {
        Ext.apply(this, {
            layout: 'anchor',
            items: [{
                xtype: 'alertmessage',
                anchor: '100%',
                cls: 'top_infobox',
                type: 'info',
                message: [this.multiselectHowto, this.multiselectWhy].join(' ')
            }, {
                xtype: 'container',
                anchor: '100%',
                layout: 'column',
                items: [{
                    xtype: 'singlegroupmetainfo',
                    columnWidth: 1,
                    groupRecord: this.groupRecord
                }, {
                    xtype: 'container',
                    width: 250,
                    padding: '0 0 0 30',
                    layout: 'anchor',
                    defaults: {
                        margin: '20 0 0 0',
                        anchor: '100%'
                    },
                    items: [{
                        xtype: 'managestudentsonsingle',
                        margin: '0 0 0 0',
                        studentsStore: this.studentsStore
                    }, {
                        xtype: 'manageexaminersonsingle',
                        examinersStore: this.examinersStore
                    }, {
                        xtype: 'managetagsonsingle',
                        tagsStore: this.tagsStore
                    }]
                }]
            }, {
                xtype: 'box',
                cls: 'bootstrap',
                itemId: 'header',
                tpl: '<h3>{heading}</h3>',
                data: {
                    heading: gettext('Deadlines and deliveries')
                }
            }, {
                xtype: 'admingroupinfo_deadlinescontainer'
            }]
        });
        this.callParent(arguments);
    }
});
