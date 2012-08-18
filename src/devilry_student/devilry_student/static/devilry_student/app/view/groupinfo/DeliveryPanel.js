Ext.define('devilry_student.view.groupinfo.DeliveryPanel' ,{
    extend: 'Ext.panel.Panel',
    alias: 'widget.groupinfo_delivery',
    //ui: 'lookslike-parawitheader-panel',
    margin: '40 20 20 20',
    requires: [
        'devilry_extjsextras.DatetimeHelpers'
    ],

    /**
     * @cfg {Object} [delivery]
     */

    /**
     * @cfg {Object} [active_feedback]
     */

    metaTpl: [
        '<tpl if="latest_feedback">',
            '<h4>', gettext('Grade') ,'</h4>',
            '<p>',
                '<tpl if="latest_feedback.is_passing_grade">',
                    '<span class="success">', gettext('Passed') ,'</span>',
                '<tpl else>',
                    '<span class="danger">', gettext('Failed') ,'</span>',
                '</tpl>',
                ' <small>({latest_feedback.grade})</small>',
            '</p>',
        '</tpl>',

        '<h4>', gettext('Time of delivery'), '</h4>',
        '<p>',
            '<tpl if="delivery.after_deadline">',
                '<span class="danger">',
                    gettext('{offset} AFTER the deadline.'),
                '</span>',
            '<tpl else>',
                gettext('{offset} before the deadline.'),
            '</tpl>',
            '<br/><small>({delivery.time_of_delivery})</small>',
        '</p>',

        '<h4>', gettext('Delivery made by'), '</h4>',
        '<p>{delivery.delivered_by.user.displayname}</p>',

        '<h4>', gettext('Files'), '</h4>',
        '<ul>',
            '<tpl for="delivery.filemetas">',
                '<li><a href="{download_url}" class="filename">{filename}</a> <small class="filesize">({pretty_size})</small></li>',
            '</tpl>',
        '</ul>',
        '<a href="{delivery.download_all_url.zip}">', gettext('Download all files'), '</a>'
    ],

    feedbackTpl: [
        '<tpl if="latest_feedback">',
            '{latest_feedback.rendered_view}',
        '<tpl else>',
            '<p><small>', gettext('No feedback'), '</small></p>',
        '</tpl>'  
    ],

    headerTpl: [
        '{delivery_text}: {delivery.number}'
    ],

    initComponent: function() {
        var latest_feedback = this.delivery.feedbacks[0];
        var has_active_feedback = this.active_feedback && this.active_feedback.delivery_id == this.delivery.id;

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
                    offset: devilry_extjsextras.DatetimeHelpers.formatTimedeltaShort(this.delivery.offset_from_deadline),
                    feedback_term: gettext('feedback'),
                    examiner_term: gettext('examiner'),
                    downloadAllUrl: this._getDownloadAllUrl()
                }
            }, {
                xtype: 'box',
                columnWidth: 0.7,
                tpl: this.feedbackTpl,
                itemId: 'feedback',
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
