Ext.define('devilry_extjsextras.DatetimeHelpers', {
    singleton: true,

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
