Ext.define('devilry_subjectadmin.view.managestudents.ExaminersHelp', {
    singleton: true,


    _introText: interpolate(gettext('%(Examiners_term)s are the ones that give feedback to students on their %(deliveries_term)s.'), {
        Examiners_term: gettext('Examiners'),
        deliveries_term: gettext('deliveries')
    }, true),

    getIntroText: function() {
        return this._introText;
    },

    _detailList: [
        interpolate(gettext('Administrators can not give feedback. If you want to give feedback to any %(groups_term)s, you have to make yourself %(examiner_term)s on those %(groups_term)s.'), {
            groups_term: gettext('groups'),
            examiner_term: gettext('examiner')
        }, true),
        interpolate(gettext('An %(examiner_term)s can open/close their %(groups_term)s.'), {
            examiner_term: gettext('examiner'),
            groups_term: gettext('groups')
        }, true),
        interpolate(gettext('An %(examiner_term)s can add new %(deadlines_term)s to their %(groups_term)s.'), {
            examiner_term: gettext('examiner'),
            deadlines_term: gettext('deadlines'),
            groups_term: gettext('groups')
        }, true),
        interpolate(gettext('A %(group_term)s can have multiple %(examiners_term)s.'), {
            group_term: gettext('group'),
            examiners_term: gettext('examiners')
        }, true),
        interpolate(gettext('Removing an %(examiner_term)s from a %(group_term)s does NOT remove any feedback already provided by that %(examiner_term)s.'), {
            examiner_term: gettext('examiner'),
            group_term: gettext('group')
        }, true)
    ],

    getDetailsUl: function() {
        if(Ext.isEmpty(this._detailsUl)) {
            this._detailsUl = Ext.create('Ext.XTemplate', 
                '<ul>',
                    '<tpl for="list">',
                        '<li>{.}</li>',
                    '</tpl>',
                '</ul>'
            ).apply({
                list: this._detailList
            });
        }
        return this._detailsUl;
    },

    getRelatedNote: function(period_id) {
        if(Ext.isEmpty(this._relatedNoteTpl)) {
            this._relatedNoteTpl = Ext.create('Ext.XTemplate', 
                '<p><small class="muted">',
                    gettext('Only <a {relatedexaminers_link}>{examiners_term} registered on the {period_term}</a> are available.'),
                '</small></p>'
            );
        }
        return this._relatedNoteTpl.apply({
            examiners_term: gettext('examiners'),
            period_term: gettext('period'),
            relatedexaminers_link: Ext.String.format('href="{0}" target="_blank"',
                devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(period_id))
        });
    }
});
