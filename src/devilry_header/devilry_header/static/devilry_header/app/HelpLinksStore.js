Ext.define('devilry_header.HelpLinksStore', {
    extend: 'Ext.data.Store',
    model: 'devilry_header.HelpLinkModel',

    getHelpLinksForUser: function(userInfoRecord) {
        var helpLinkRecords = [];
        this.each(function(helpLinkRecord) {
            if(helpLinkRecord.matchesUserInfoRecord(userInfoRecord)) {
                helpLinkRecords.push(helpLinkRecord);
            }
        }, this);
        return helpLinkRecords;
    }
});
