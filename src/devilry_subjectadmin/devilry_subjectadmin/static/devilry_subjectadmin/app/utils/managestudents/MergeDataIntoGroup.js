Ext.define('devilry_subjectadmin.utils.managestudents.MergeDataIntoGroup', {
    singleton: true,

    requires: [
        'devilry_subjectadmin.utils.Array'
    ],

    /**
     * Merge tags into groupRecord.
     *
     * @param {devilry_subjectadmin.model.Group} [groupRecord] Group record.
     * @param {[String]} [sourceTags] Array of tags. Each item is a string.
     * @param {Boolean} [doNotDeleteTags=false] Set this to ``true`` to append to existing tags.
     */
    mergeTags: function(groupRecord, sourceTags, doNotDeleteTags) {
        var tags = [];
        var currentTags = groupRecord.get('tags');
        devilry_subjectadmin.utils.Array.mergeIntoArray({
            destinationArray: currentTags,
            sourceArray: sourceTags,
            isEqual: function(tagObj, sourceTagString) {
                return tagObj.tag == sourceTagString;
            },
            onMatch: function(tagObj) {
                tags.push(tagObj);
            },
            onNoMatch: function(tagObj) {
                if(doNotDeleteTags) {
                    tags.push(tagObj);
                }
            },
            onAdd: function(sourceTagString) {
                tags.push({
                    tag: sourceTagString
                });
            }
        });
        groupRecord.set('tags', tags);
    }
});
