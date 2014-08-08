Ext.define('devilry_qualifiesforexam.model.Preview', {
    extend: 'Ext.data.Model',

    fields: [
        {name: 'pluginoutput',  type: 'auto', pesist: false},
        {name: 'perioddata', type: 'auto', pesist: false}
    ],

    proxy: {
        type: 'rest',
        urlformat: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_qualifiesforexam/rest/preview/{0}',
        appendId: false,
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    statics: {
        setParamsAndLoad: function(periodid, pluginsessionid, config) {
            this.proxy.extraParams.pluginsessionid = pluginsessionid;
            this.proxy.url = Ext.String.format(this.proxy.urlformat, periodid);
            this.load(null, config);
        }
    }
});
