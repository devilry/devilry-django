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
        'devilry_subjectadmin.view.managestudents.TagsInGroupGrid'
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

    metaInfoTpl: [
        '<dl>',
            '<dt>', pgettext('group', 'Grade') ,':</dt> ',
            '<dd>',
                '<tpl if="hasFeedback">',
                    '{feedback.grade} ',
                    '<tpl if="feedback.is_passing_grade"><span class="label label-success">',
                        pgettext('group', 'Passed'),
                    '</span></tpl>',
                    '<tpl if="!feedback.is_passing_grade"><span class="label label-warning">',
                        pgettext('group', 'Failed'),
                    '</span></tpl>',
                    ' <span class="label">',
                        pgettext('group', 'Points'), ': {feedback.points}',
                    '</span>',
                '</tpl>',
                '<tpl if="!hasFeedback"><span class="label label-info">',
                    gettext('No feedback'),
                '</span></tpl>',
            '</dd>',

            '<dt>', Ext.String.capitalize(gettext('Deliveries')) ,':</dt> ',
            '<dd>{num_deliveries}</dd>',

            '<dt>', gettext('Status'), ':</dt>',
            '<dd>',
                '<tpl if="is_open">',
                    '<span class="label label-success">', pgettext('group', 'Open'), '</span> ',
                    gettext('The student(s) can add more deliveries.'),
                '</tpl>',
                '<tpl if="!is_open">',
                    '<span class="label label-warning">', pgettext('group', 'Closed'), '</span> ',
                    gettext('The current grade is the final grade. The student(s) can <strong>not</strong> add more deliveries.'),
                '</tpl>',
                ' ', gettext('Examiners can open and close a group at any time to allow/prevent deliveries.'),
            '</dd>',
        '</dl>'
    ],

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
                    columnWidth: 1,
                    items: [{
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: this._getMetaInfo()
                    }, {
                        xtype: 'box',
                        cls: 'bootstrap',
                        html: '<strong>NOTE:</strong> This view is incomplete. Please see <a href="http://heim.ifi.uio.no/espeak/devilry-figures/managestudents-singleselect.png" target="_blank">this image mockup</a> of the planned interface.'
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
                        examinersStore: this.examinersStore
                    }, {
                        xtype: 'tagsingroupgrid',
                        store: this.tagsStore
                    }]
                }]
            }]
        });
        this.callParent(arguments);
    },

    _getMetaInfo: function() {
        var tpl = Ext.create('Ext.XTemplate', this.metaInfoTpl);
        var data = Ext.apply({
            hasFeedback: this.groupRecord.get('feedback') != null,
            passing_grade_i18n: pgettext('group', 'Passed'),
            not_passing_grade_i18n: pgettext('group', 'Failed'),
            points_i18n: pgettext('group', 'Points')
        }, this.groupRecord.data);
        return tpl.apply(data);
    }
});
