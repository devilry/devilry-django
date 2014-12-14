Ext.define('devilry_subjectadmin.model.RelatedUserBase', {
    extend: 'Ext.data.Model',

    getTagsAsArray: function() {
        var tags = this.get('tags');
        if(Ext.isEmpty(tags)) {
            return [];
        } else {
            return tags.split(',');
        }
    },

    clearTags: function() {
        this.set('tags', '');
    },

    /** Set tags from an array. */
    setTagsFromArray: function(tagsArray) {
        this.set('tags', tagsArray.join(','));
    },

    /** Add the tags in ``newTagsArray`` to the current tags, ignoring any
     * duplicates. */
    addTagsFromArray: function(newTagsArray) {
        var tagsArray = Ext.Array.union(this.getTagsAsArray(), newTagsArray);
        this.setTagsFromArray(tagsArray);
    },

    getDisplayName: function() {
        return this.get('user').displayname;
    },

    statics: {
        recordsAsDisplaynameArray: function(records) {
            var names = [];
            Ext.Array.each(records, function(relatedUserRecord) {
                var displayname = relatedUserRecord.getDisplayName();
                names.push(displayname);
            }, this);
            return names;
        }
    }
});
