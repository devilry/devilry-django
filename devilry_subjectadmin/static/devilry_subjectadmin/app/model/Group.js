/**
 * Group-model for the ``/subjectadmin/rest/group`` API.
 */
Ext.define('devilry_subjectadmin.model.Group', {
    extend: 'Ext.data.Model',
    idProperty: 'id',
    fields: [
        {name: 'id', type: 'int'},
        {name: 'num_deliveries', type: 'int', persist: false},
        {name: 'name',  type: 'string'},
        {name: 'is_open',  type: 'boolean'},
        {name: 'tags', type: 'auto'},
        {name: 'feedback',  type: 'auto'},
        {name: 'candidates', type: 'auto'},
        {name: 'examiners', type: 'auto'},
        {name: 'deadlines', type: 'auto'},
        {name: 'status', type: 'string', persist: false}
    ],

    proxy: {
        type: 'rest',
        urlpatt: DevilrySettings.DEVILRY_URLPATH_PREFIX + '/devilry_subjectadmin/rest/group/{0}/',
        url: null, // We use urlpatt to dynamically generate the url
        batchActions: true,
        appendId: false, 
        extraParams: {
            format: 'json'
        },
        reader: {
            type: 'json'
        }
    },

    _debugFormatArray: function(array, tpl) {
        var itemtpl = Ext.create('Ext.XTemplate', tpl);
        var items = [];
        Ext.Array.each(array, function(item, index) {
            items.push('\n    ' + index + ': {' + itemtpl.apply(item) + '}');
        }, this);
        return items.join(', ');
    },

    debugFormat: function() {
        var usertpl = [
            'id:{id}, ',
            '<tpl if="candidate_id">candidate_id:{candidate_id}, </tpl>',
            'user.id:{user.id}, username:{user.username}, full_name:{user.full_name}, email:{user.email}'
        ];
        var tagtpl = ['id:{id}, tag:{tag}'];
        return Ext.String.format('id={0}, num_deliveries={1}, name={2}, is_open={3},\n- tags=[{4}],\n- candidates=[{5}],\n- examiners=[{6}]',
            this.get('id'),
            this.get('num_deliveries'),
            this.get('name'),
            this.get('is_open'),
            this._debugFormatArray(this.get('tags'), tagtpl),
            this._debugFormatArray(this.get('candidates'), usertpl),
            this._debugFormatArray(this.get('examiners'), usertpl)
        );
    },


    _getUserNamesAsArray: function(users) {
        var names = [];
        Ext.Array.each(users, function(user, index) {
            if(user.user.full_name) {
                names.push(user.user.full_name);
            } else {
                names.push(user.user.username);
            }
        }, this);
        return names;
    },

    getCandidateNamesAsArray: function() {
        return this._getUserNamesAsArray(this.get('candidates'));
    },

    /** Get a string that should be usable to identify a group.
     * If the group has any candidates, use #getCandidateNamesAsArray, else
     * return the ID of the group.
     * */
    getIdentString: function() {
        if(this.get('candidates')) {
            return this.getCandidateNamesAsArray().join(', ');
        } else {
            return this.get('id');
        }
    },


    /** Return ``true`` if the given ``userid`` is in ``examiners``. */
    hasExaminer: function(userid) {
        return Ext.Array.some(this.get('examiners'), function(examiner) {
            return examiner.user.id == userid;
        });
    },

    /** Return ``true`` if the given ``tag`` is in ``tags``. */
    hasTag: function(tag) {
        return Ext.Array.some(this.get('tags'), function(tagObj) {
            return tagObj.tag == tag;
        });
    },


    /**
     * Set ``tags`` from an array of strings, where each string is a tag.
     */
    setTagsFromArrayOfStrings: function(tagsAsStrings) {
        var tags = [];
        Ext.Array.each(tagsAsStrings, function(tagString) {
            tags.push({
                tag: tagString
            });
        }, this);
        this.set('tags', tags);
    },

    setExaminersFromArrayOfUserIds: function(userids) {
        var examiners = [];
        for(var index=0; index<userids.length; index++)  {
            var userid = userids[index];
            examiners.push({
                user: {id: userid}
            });
        }
        this.set('examiners', examiners);
    },

    /**
     * Set examiners by matching tags on examiners with ``this.get('tags')``.
     *
     * @param {Object} [relatedExaminersMappedByTag]
     *      Like the one returned by getMappedByTags() in AbstractRelatedUsers.
     */
    setExaminersFromMapOfRelatedExaminers: function(relatedExaminersMappedByTag) {
        var examiners = [];
        Ext.Array.each(this.get('tags'), function(tagObj) {
            var tag = tagObj.tag;
            if(relatedExaminersMappedByTag[tag]) {
                Ext.Array.each(relatedExaminersMappedByTag[tag], function(relatedExaminerRecord) {
                    var userid = relatedExaminerRecord.get('user').id;
                    examiners.push(userid);
                }, this);
            }
        }, this);
        this.setExaminersFromArrayOfUserIds(Ext.Array.unique(examiners));
    },


    statics: {
        formatIdentsAsStringList: function(groupRecords) {
            var groups = [];
            Ext.Array.each(groupRecords, function(groupRecord) {
                groups.push(groupRecord.getIdentString());
            }, this);
            return groups.join(', ');
        }
    }
});
