/** Groups on an assignment. */
Ext.define('devilry_subjectadmin.store.Groups', {
    extend: 'Ext.data.Store',
    model: 'devilry_subjectadmin.model.Group',

    setAssignment: function(assignment_id) {
        this.proxy.url = Ext.String.format(this.proxy.urlpatt, assignment_id);
    },

    loadGroupsInAssignment: function(assignment_id, loadConfig) {
        this.setAssignment(assignment_id);
        this.load(loadConfig);
    },


    sortBySpecialSorter: function(sortby) {
        var sorter = null;
        if(sortby == 'username') {
            sorter = this._sortByUsername;
        } else if(sortby == 'fullname') {
            sorter = this._sortByFullname;
        } else if(sortby == 'lastname') {
            sorter = this._sortByLastname;
        } else {
            throw "Invalid sorter: " + sortby;
        }
        this.sort(Ext.create('Ext.util.Sorter', {
            sorterFn: Ext.bind(sorter, this)
        }));
    },

    _sortByUsername: function(a, b) {
        return this._sortByUserlistProperty('candidates', 'username', a, b);
    },

    _sortByFullname: function(a, b) {
        return this._sortByUserlistProperty('candidates', 'full_name', a, b);
    },

    _sortByUserlistProperty: function(listproperty, attribute, a, b) {
        var listA = a.get(listproperty);
        var listB = b.get(listproperty);
        if(listA.length == 0) {
            return -1;
        }
        if(listB.length == 0) {
            return 1;
        }
        var a = listA[0].user[attribute];
        var b = listB[0].user[attribute];
        if(!a) {
            return -1;
        }
        if(!b) {
            return 1;
        }
        return a.localeCompare(b);
    },

    _getLastname: function(fullname) {
        var split = fullname.split(/\s+/);
        return split[split.length-1];
    },

    _sortByLastname: function(a, b) {
        var listA = a.get('candidates');
        var listB = b.get('candidates');
        if(listA.length == 0) {
            return -1;
        }
        if(listB.length == 0) {
            return 1;
        }
        var attribute = 'full_name';
        var a = this._getLastname(listA[0].user[attribute]);
        var b = this._getLastname(listB[0].user[attribute]);
        return a.localeCompare(b);
    },



    /**
     * Get the contents of the groups store with userids as key and an array of
     * {@link devilry_subjectadmin.model.Group} records as value.
     *
     * The values are arrays because we support the same user in multiple
     * groups on the same assignment.
     */
    getGroupsMappedByUserId: function() {
        var map = {}; // userid -> [groupRecord]
        this.each(function(groupRecord) {
            Ext.each(groupRecord.get('candidates'), function(candidate) {
                var userid = candidate.user.id;
                if(map[userid]) {
                    map[userid].push(groupRecord);
                } else {
                    map[userid] = [groupRecord];
                }
            }, this);
        }, this);
        return map;
    },


    addFromRelatedStudentRecord: function(config) {
        var relatedStudentRecord = config.relatedStudentRecord;
        var includeTags = config.includeTags;
        var groupRecord = this.add({
            is_open: true,
            examiners: [],
            tags: [],
            candidates: [{
                user: {
                    id: relatedStudentRecord.get('user').id
                }
            }]
        })[0];
        if(config.includeTags) {
            groupRecord.setTagsFromArrayOfStrings(relatedStudentRecord.getTagsAsArray());
        }
        return groupRecord;
    }
});
