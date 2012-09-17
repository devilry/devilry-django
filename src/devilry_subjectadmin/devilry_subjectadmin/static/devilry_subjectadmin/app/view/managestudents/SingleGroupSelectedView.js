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
        'devilry_subjectadmin.view.managestudents.SingleMetaInfo',
        'devilry_subjectadmin.view.managestudents.DeliveriesList'
    ],

    /**
     * @cfg {string} multiselectHowto (required)
     */

    /**
     * @cfg {String} [assignment_id]
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

    /**
     * @cfg {int} [period_id]
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
                    xtype: 'container',
                    layout: 'anchor',
                    defaults: {
                        anchor: '100%'
                    },
                    columnWidth: 1,
                    items: [{
                        xtype: 'singlegroupmetainfo',
                        groupRecord: this.groupRecord,
                        assignment_id: this.assignment_id
                    }, {
                        xtype: 'deliverieslist',
                        groupRecord: this.groupRecord,
                        assignment_id: this.assignment_id
                    }]
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
                        examinersStore: this.examinersStore,
                        period_id: this.period_id
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
