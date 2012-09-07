Ext.define('devilry_subjectadmin.model.RelatedUserBase', {
    extend: 'Ext.data.Model',

    getTagsAsArray: function() {
        var tags = this.get('tags') || '';
        return tags.split(',');
    },

    getDisplayName: function() {
        return this.get('user').displayname;
    }
});
