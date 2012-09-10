Ext.define('devilry_subjectadmin.view.managestudents.TagsHelp', {
    singleton: true,

    _introText: interpolate(gettext('%(Tags_term)s is a flexible method of organizing %(groups_term)s. Only administrators and %(examiners_term)s can see %(tags_term)s. You can search and select %(groups_term)s by their %(tags_term)s. Common use-cases are:'), {
        Tags_term: gettext('Tags'),
        examiners_term: gettext('examiners'),
        groups_term: gettext('groups'),
        tags_term: gettext('tags')
    }, true),

    getIntroText: function() {
        return this._introText;
    },

    
    _periodNote: interpolate(gettext('<strong>NOTE:</strong> %(Tags_term)s on %(groups_term)s must not be confused with %(tags_term)s on %(students_term)s and %(examiners_term)s on a %(period_term)s. Those %(tags_term)s are used to automate assigning examiners to students. %(Tags_term)s from the %(period_term)s may have been included when you added %(groups_term)s to this %(assignment_term)s, however you can safely edit %(tags_term)s on %(groups_term)s without affecting the %(tags_term)s on the %(period_term)s.'), {
        Tags_term: gettext('Tags'),
        groups_term: gettext('groups'),
        tags_term: gettext('tags'),
        examiners_term: gettext('examiners'),
        students_term: gettext('students'),
        period_term: gettext('period'),
        assignment_term: gettext('assignment')
    }, true),

    getPeriodNote: function() {
        return this._periodNote;
    },


    _detailList: [
        interpolate(gettext('Mark %(groups_term)s with special needs.'), {
            groups_term: gettext('groups')
        }, true),
        interpolate(gettext('Organize %(groups_term)s attending the same classroom sessions.'), {
            groups_term: gettext('groups')
        }, true),
        gettext('Mark suspected cheaters.')
    ],

    getDetailsUl: function() {
        if(Ext.isEmpty(this.ul)) {
            this._detailsUl = Ext.create('Ext.XTemplate', 
                '<ul>',
                    '<tpl for="points">',
                        '<li>{.}</li>',
                    '</tpl>',
                '</ul>'
            ).apply({
                points: this._detailList
            });
        }
        return this._detailsUl;
    }
});
