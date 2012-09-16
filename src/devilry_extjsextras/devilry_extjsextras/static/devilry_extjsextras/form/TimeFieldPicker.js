Ext.define('devilry_extjsextras.form.TimeFieldPicker', {
    extend: 'Ext.picker.Time',
    alias: 'widget.devilry_extjsextras_timefieldpicker',
    cls: 'devilry_extjsextras_timefieldpicker',

    requires: [
        'Ext.Date',
        'Ext.util.MixedCollection'
    ],

    /**
     * @cfg {String[]} [specialTimes]
     * Array of times that appears emphasized at the top of the list.
     * The format is ``hh:mm``.
     */
    specialTimes: [
        '12:00',
        '13:00',
        '14:00',
        '15:00',
        '16:00',
        '23:59'
    ],

    initComponent: function() {
        var me = this;
        this.tpl = Ext.create('Ext.XTemplate',
            '<ul><tpl for=".">',
                '<li role="option" class="' + this.itemCls + '">',
                    '<tpl if="isSpecial">',
                        '<tpl if="isLastSpecial">',
                            '<div style="margin-bottom: 6px;">',
                                '<strong>{disp}</strong>',
                            '<div>',
                        '<tpl else>',
                            '<strong>{disp}</strong>',
                        '</tpl>',
                    '<tpl else>',
                        '{disp}',
                    '</tpl>',
                '</li>',
            '</tpl></ul>'
        );
        this.callParent(arguments);
    },

    _createSpecialTimesMap: function() {
        var specialTimesMap = new Ext.util.MixedCollection();
        return specialTimesMap;
    },

    _addSpecialTimes: function(timesArray) {
        Ext.Array.each(this.specialTimes, function(timestring, index) {
            var dateobj = this._parseTimeStringToDateObj(timestring);
            var formatted = Ext.Date.format(dateobj, this.format);
            timesArray.push({
                disp: formatted,
                date: dateobj,
                isSpecial: true,
                isLastSpecial: (index == this.specialTimes.length-1)
            });
        }, this);
    },

    _addAutoIncrementedTimes: function(timesArray) {
        var min = this.absMin;
        var max = this.absMax;
        while(min <= max){
            timesArray.push({
                disp: Ext.Date.dateFormat(min, this.format),
                date: min
            });
            min = Ext.Date.add(min, 'mi', this.increment);
        }
    },

    createStore: function() {
        var me = this;
        var timesArray = [];
        this._addSpecialTimes(timesArray);
        this._addAutoIncrementedTimes(timesArray);
        return new Ext.data.Store({
            fields: [
                {name: 'disp', type: 'string'},
                {name: 'date', type: 'date'},
                {name: 'isSpecial', type: 'bool', defaultValue: false},
                {name: 'isLastSpecial', type: 'bool', defaultValue: false}
            ],
            data: timesArray
        });
    },

    /* Get a time-string (like in ``specialTimes``), and return the number of minutes from 00:00. */
    _parseTimeStringToDateObj: function(timestring) {
        var dateobj = Ext.Date.parse(timestring, 'H:i', true);
        return this._getTimeByMinuteOffset(dateobj.getHours() * 60 + dateobj.getMinutes());
    },

    _getTimeByMinuteOffset: function(minutes) {
        return Ext.Date.add(this.absMin, Ext.Date.MINUTE, minutes);
    }
});
