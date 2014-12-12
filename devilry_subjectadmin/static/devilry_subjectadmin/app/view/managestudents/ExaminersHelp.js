Ext.define('devilry_subjectadmin.view.managestudents.ExaminersHelp', {
    singleton: true,


    _introText: gettext('Examiners are the ones that give feedback to students on their deliveries.'),

    getIntroText: function() {
        return this._introText;
    },

    _detailList: [
        gettext('Administrators can not give feedback. If you want to give feedback to any groups, you have to make yourself examiner on those groups.'),
        gettext('An examiner can open/close their groups.'),
        gettext('An examiner can add new deadlines to their groups.'),
        gettext('A group can have multiple examiners.'),
        gettext('Removing an examiner from a group does NOT remove any feedback already provided by that examiner.')
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
                    gettext('Only <a {relatedexaminers_link}>examiners registered on the {period_term}</a> are available.'),
                '</small></p>'
            );
        }
        return this._relatedNoteTpl.apply({
            period_term: gettext('period'),
            relatedexaminers_link: Ext.String.format('href="{0}" target="_blank" class="new-window-link"',
                devilry_subjectadmin.utils.UrlLookup.manageRelatedExaminers(period_id))
        });
    }
});
