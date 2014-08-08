Ext.define('devilry_extjsextras.DatetimeHelpers', {
    singleton: true,
    requires: [
        'Ext.Date'
    ],

    /**
     * Format the given Date object in a human readable string suitable for places where
     * space is an issue.
     *
     * @param dateobj A Date object.
     */
    formatDateTimeShort: function(dateobj) {
        return Ext.Date.format(dateobj, pgettext('extjs short datetime', 'Y-m-d H:i'));
    },

    /**
     * Format the given Date object in a human readable string suitable for places where
     * space is not an issue.
     *
     * @param dateobj A Date object.
     */
    formatDateTimeLong: function(dateobj) {
        return Ext.Date.format(dateobj, pgettext('extjs long datetime', 'Y-m-d H:i'));
    },

    parseRestformattedDatetime: function (datetimeString) {
//        return Ext.Date.parse(datetimeString, 'Y-m-dTH:i:s.u');
        return Ext.Date.parse(datetimeString, 'c');
    },

    /**
     * Format a time ``delta`` as a human readable string.
     *
     * @param delta An object with the following attributes ``days``, ``hours``, ``minutes`` and ``seconds``
     */
    formatTimedeltaShort: function(delta) {
        if(delta.days > 0) {
            return interpolate(gettext('%s days'), [delta.days]);
        } else if(delta.hours > 0) {
            return interpolate(gettext('%s hours'), [delta.hours]);
        } else if(delta.minutes > 0) {
            return interpolate(gettext('%s minutes'), [delta.minutes]);
        } else {
            return interpolate(gettext('%s seconds'), [delta.seconds]);
        }
    },

    /**
     * Format a time ``delta`` as a human readable string relative to *now*.
     *
     * @param delta An object with the following attributes ``days``, ``hours``, ``minutes`` and ``seconds``
     * @param in_the_future Is the delta positive? Defaults to ``false``, which means that we
     *      the result is a string that indicates past tense.
     */
    formatTimedeltaRelative: function(delta, in_the_future) {
        if(in_the_future) {
            return interpolate(gettext('In %(delta)s'), {
                delta: this.formatTimedeltaShort(delta)
            }, true);
        } else {
            return interpolate(gettext('%(delta)s ago'), {
                delta: this.formatTimedeltaShort(delta)
            }, true);
        }
    }
});
