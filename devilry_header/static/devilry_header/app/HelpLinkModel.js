Ext.define('devilry_header.HelpLinkModel', {
    extend: 'Ext.data.Model',
    idProperty: 'url',
    fields: [
        {name: 'help_url', type: 'string'},
        {name: 'title', type: 'string'},
        {name: 'description', type: 'string'},
        {name: 'superuser', type: 'bool'},
        {name: 'nodeadmin', type: 'bool'},
        {name: 'subjectadmin', type: 'bool'},
        {name: 'periodadmin', type: 'bool'},
        {name: 'assignmentadmin', type: 'bool'},
        {name: 'examiner', type: 'bool'},
        {name: 'student', type: 'bool'}
    ],

    proxy: {
        type: 'rest',
        url: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_helplinks/helplinks/',
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },
    
    roles: ['superuser', 'nodeadmin', 'subjectadmin', 'periodadmin',
        'assignmentadmin', 'examiner', 'student'],

    matchesUserInfoRecord: function(userInfoRecord) {
        for(var i=0; i < this.roles.length; i++)  {
            var role = this.roles[i];
            if(this.get(role) && userInfoRecord.get('is_' + role)) {
                return true;
            }
        }
    }
});
