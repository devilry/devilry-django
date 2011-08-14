Ext.define('devilry.gradeeditors.EditManyDraftEditorWindow', {
    extend: 'devilry.gradeeditors.DraftEditorWindow',

    constructor: function(config) {
        this.callParent([config]);
        this.addEvents('createNewDraft');
    },

    /**
     * Not allowed in EditManyDraftEditorWindow.
     */
    saveDraft: function(draftstring, onFailure) {
        throw "Save draft is not allowed in EditManyDraftEditorWindow.";
    },

    /**
     * Fire createNewDraft event with the draft string as argument.
     *
     * @param draftstring The draftstring.
     */
    saveDraftAndPublish: function(draftstring, onFailure) {
        this.fireEvent('createNewDraft', draftstring);
    }
});
