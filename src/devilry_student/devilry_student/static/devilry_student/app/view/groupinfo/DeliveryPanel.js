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
        '<tpl if="latest_feedback">',
            '<h3>', gettext('Grade') ,'</h3>',
            '<p>',
                '<tpl if="latest_feedback.is_passing_grade">',
                    '<span class="success">', gettext('Passed') ,'</span>',
                '<tpl else>',
                    '<span class="danger">', gettext('Failed') ,'</span>',
                '</tpl>',
                ' <small>({latest_feedback.grade})</small>',
            '</p>',
        '</tpl>',

        '<h3>', gettext('Time of delivery'), '</h3>',
        '<p>',
            '<tpl if="delivery.after_deadline">',
                '<span class="danger">',
                    gettext('{offset.days} days, {offset.hours} hours, {offset.minutes} min and {offset.seconds} seconds AFTER the deadline.'),
                '</span>',
            '<tpl else>',
                gettext('{offset.days} days, {offset.hours} hours, {offset.minutes} minutes and {offset.seconds} seconds before the deadline.'),
            '</tpl>',
            '<br/><small>({delivery.time_of_delivery})</small>',
        '</p>',

        '<h3>', gettext('Delivery made by'), '</h3>',
        '<p>{delivery.delivered_by.user.displayname}</p>',

        '<h3>', gettext('Files'), '</h3>',
        '<ul>',
            '<tpl for="delivery.filemetas">',
                '<li><a href="{download_url}" class="filename">{filename}</a> <small class="filesize">({pretty_size})</small></li>',
            '</tpl>',
        '</ul>',
        '<a href="{delivery.download_all_url.zip}">', gettext('Download all files'), '</a>',
        '<tpl if="has_active_feedback">',
            '<p>',
                gettext('This is the active {feedback_term}. This feedback is the one that counts for this assignment unless an {examiner_term} makes a new {feedback_term}.'),
            '</p>',
        '</tpl>'
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

        //var metaTplCompiled = Ext.create('Ext.XTemplate', this.metaTpl, {
            //getFileDownloadUrl: Ext.bind(this._getFileDownloadUrl, this)
        //});

        Ext.apply(this, {
            ui: has_active_feedback? 'inset-header-strong-panel': 'inset-header-panel',
            cls: 'devilry_student_groupinfo_delivery devilry_student_groupinfo_delivery_' + (this._hasFeedback()? 'hasfeedback': 'nofeedback'),
            title: Ext.create('Ext.XTemplate', this.headerTpl).apply({
                delivery_text: gettext('Delivery'),
                delivery: this.delivery
            }),
            itemId: Ext.String.format('delivery-{0}', this.delivery.id),
            layout: 'column',
            items: [{
                columnWidth: 0.3,
                xtype: 'box',
                cls: 'bootstrap devilry_student_groupinfo_delivery_meta',
                itemId: 'meta',
                tpl: this.metaTpl,
                data: {
                    delivery: this.delivery,
                    latest_feedback: latest_feedback,
                    has_active_feedback: has_active_feedback,
                    offset: this.delivery.offset_from_deadline,
                    feedback_term: gettext('feedback'),
                    examiner_term: gettext('examiner'),
                    downloadAllUrl: this._getDownloadAllUrl()
                }
            }, {
                xtype: 'box',
                columnWidth: 0.7,
                tpl: this.feedbackTpl,
                itemid: 'feedback',
                cls: 'bootstrap devilry_student_groupinfo_delivery_rendered_view',
                padding: '0 0 0 40',
                data: {
                    latest_feedback: latest_feedback
                }
            }]
        });
        this.callParent(arguments);
    },

    _hasFeedback: function() {
        return this.delivery.feedbacks.length > 0;
    },

    _getDownloadAllUrl: function() {
        return Ext.String.format(
            '{0}/student/show-delivery/compressedfiledownload/{1}',
            DevilrySettings.DEVILRY_URLPATH_PREFIX, this.delivery.id
        );
    }
});
