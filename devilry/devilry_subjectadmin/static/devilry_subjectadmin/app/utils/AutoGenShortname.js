Ext.define('devilry_subjectadmin.utils.AutoGenShortname', {
    singleton: true,

    charcodes: {
        space: 32,
        dash: 45,
        underscore: 95,
        a: 97,
        z: 122,
        zero: 48,
        nine: 57
    },

    _inRange: function(value, a, b) {
        return value >= a && value <= b;
    },

    autogenShortname: function(long_name) {
        var short_name = '';
        long_name = long_name.toLowerCase();
        for(var index=0; index<long_name.length; index++)  {
            var charcode = long_name.charCodeAt(index);
            var charvalue = long_name.charAt(index);
            var isAsciiLetter = this._inRange(charcode, this.charcodes.a, this.charcodes.z);
            var isNumber = this._inRange(charcode, this.charcodes.zero, this.charcodes.nine);
            var isValidSpecial = charcode == this.charcodes.dash || charcode == this.charcodes.underscore;
            var isSpace = charcode == this.charcodes.space;
            if(isAsciiLetter || isNumber || isValidSpecial) {
                short_name += charvalue;
            } else if(isSpace) {
                short_name += '-';
            }
        }
        if(short_name.length < 20 && short_name.length > long_name.length/2) {
            return short_name;
        } else {
            return '';
        }
    }
});
