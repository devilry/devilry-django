Ext.define('devilry_subjectadmin.view.managestudents.TagsHelp', {
    singleton: true,

    _introText: gettext('Tags is a flexible method of organizing groups. Only administrators and examiners can see tags. You can search and select groups by their tags. Common use-cases are:'),

    getIntroText: function() {
        return this._introText;
    },

    
    _periodNote: gettext('<strong>NOTE:</strong> Tags on groups must not be confused with tags on students and examiners on a term. Those tags are used to automate assigning examiners to students. Tags from the term may have been included when you added groups to this assignment, however you can safely edit tags on groups without affecting the tags on the term.'),

    getPeriodNote: function() {
        return this._periodNote;
    },


    _detailList: [
        gettext('Mark groups with special needs.'),
        gettext('Organize groups attending the same classroom sessions.'),
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
