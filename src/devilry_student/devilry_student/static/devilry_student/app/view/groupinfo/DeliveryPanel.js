Ext.define('devilry_student.view.groupinfo.DeliveryPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo_delivery',
    //ui: 'lookslike-parawitheader-panel',
    margin: '40 20 20 20',

    /**
     * @cfg {Object} [delivery]
     */

    /**
     * @cfg {Object} [active_feedback]
     */

    metaTpl: [
        '<dl>',
            '<tpl if="latest_feedback">',
                '<dt>', gettext('Grade') ,'</dt>',
                '<dd>',
                    '<tpl if="latest_feedback.is_passing_grade">',
                        '<span class="success">', gettext('Passed') ,'</span>',
                    '<tpl else>',
                        '<span class="danger">', gettext('Failed') ,'</span>',
                    '</tpl>',
                    ' <small>({latest_feedback.grade})</small>',
                '</dd>',
            '</tpl>',

            '<dt>', gettext('Time of delivery'), '</dt>',
            '<dd>',
                '<p>{delivery.time_of_delivery}</p>',
                '<tpl if="delivery.after_deadline">',
                    '<p><span class="danger">',
                        gettext('{offset.days} days, {offset.hours} hours, {offset.minutes} min and {offset.seconds} seconds AFTER the deadline'),
                    '</span></p>',
                '<tpl else>',
                    '<small>',
                        gettext('{offset.days} days, {offset.hours} hours, {offset.minutes} minutes and {offset.seconds} seconds before the deadline'),
                    '</small>',
                '</tpl>',
            '</dd>',

            '<dt>', gettext('Delivery made by'), '</dt>',
            '<dd>{delivery.delivered_by.user.displayname}</dd>',

            '<dt>', gettext('Files'), '</dt>',
            '<dd>',
                '<ul>',
                    '<tpl for="delivery.filemetas">',
                        '<li><a href="#" class="filename">{filename}</a> <small class="filesize">({pretty_size})</small></li>',
                    '</tpl>',
                '</ul>',
                '<a href="#">', gettext('Download all files'), '</a>',
            '</dd>',
            '<tpl if="has_active_feedback">',
                '<p>',
                    gettext('This is the active {feedback_term}. This feedback is the one that counts for this assignment unless an {examiner_term} makes a new {feedback_term}.'),
                '</p>',
            '</tpl>',
            
        '</dl>',
    ],

    feedbackTpl: [
        '<tpl if="latest_feedback">',
            '{latest_feedback.rendered_view}',
        '<tpl else>',
            gettext('No feedback'),
        '</tpl>'  
    ],

    headerTpl: [
        '{delivery_text}: {delivery.number}'
    ],

    initComponent: function() {
        var latest_feedback = this.delivery.feedbacks[0];
        var has_active_feedback = this.active_feedback.delivery_id == this.delivery.id;
        Ext.apply(this, {
            ui: has_active_feedback? 'inset-header-strong-panel': 'inset-header-panel',
            cls: 'devilry_student_groupinfo_delivery devilry_student_groupinfo_delivery_' + (this._hasFeedback()? 'hasfeedback': 'nofeedback'),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                delivery_text: gettext('Delivery'),
                delivery: this.delivery
            }),
            layout: 'column',
            items: [{
                width: 250,
                xtype: 'box',
                tpl: this.metaTpl,
                cls: 'bootstrap devilry_student_groupinfo_delivery_meta',
                itemId: 'meta',
                data: {
                    delivery: this.delivery,
                    latest_feedback: latest_feedback,
                    has_active_feedback: has_active_feedback,
                    offset: this.delivery.offset_from_deadline,
                    feedback_term: gettext('feedback'),
                    examiner_term: gettext('examiner')
                }
            }, {
                xtype: 'box',
                columnWidth: 1,
                tpl: this.feedbackTpl,
                itemid: 'feedback',
                cls: 'bootstrap devilry_student_groupinfo_delivery_rendered_view',
                padding: '0 0 0 40',
                data: {
                    latest_feedback: latest_feedback
                }
            }]
        });
        console.log(this.delivery.filemetas);
        this.callParent(arguments);
    },

    _hasFeedback: function() {
        return this.delivery.feedbacks.length > 0;
    }
});
