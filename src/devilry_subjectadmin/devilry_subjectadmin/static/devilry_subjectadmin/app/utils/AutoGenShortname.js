Ext.define('devilry_subjectadmin.utils.AutoGenShortname', {
    singleton: true,

    charcodes: {
        space: 32,
        dash: 45,
        underscore: 95,
        a: 97,
        z: 122
    },

    autogenShortname: function(long_name) {
        var short_name = '';
        long_name = long_name.toLowerCase();
        for(var index=0; index<long_name.length; index++)  {
            var charcode = long_name.charCodeAt(index);
            var charvalue = long_name.charAt(index);
            var isAsciiLetter = charcode >= this.charcodes.a && charcode <= this.charcodes.z;
            if(isAsciiLetter) {
                short_name += charvalue;
            } else if(charcode == this.charcodes.space) {
                short_name += '-';
            } else if(charcode == this.charcodes.dash || charcode == this.charcodes.underscore) {
                short_name += charvalue;
            }
        }
        return short_name;
    }
});
