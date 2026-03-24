/**
 * Handles comment-form related features for the feedbackfeed.
 * 
 * This class maintains a "state" that is relevant to notify the user 
 * when navigation-related actions are applied, such as warning if the 
 * user has any unpublished content by using the standard built-in browser 
 * prompt.
 * 
 * An edge-case that is also handled is 
 * ensuring that submitting the form applies the default behaviour of posting 
 * the form without the user being interrupted by a prompt.
 * 
 * Comment-form related features that are handled:
 *  - If the comment-editor has content, the user is prompted before navigation or reload is applied.
 *  - If files are uploaded or are being processed, the user is prompted before navigation or reload is applied.
 *  - When the form is submitted, the default behaviour is applied, and the user is not prompted.
 */
export class DevilryFeedbackfeedbNavigationHandler {
    constructor (windowChangeConfirmMessage) {
        this.windowChangeConfirmMessage = windowChangeConfirmMessage;

        this.addWindowNavigationListener();
        this.addFormSubmitListener();
        this.addCommentEditorContentListener();
        this.addFileuploadContentListener();

        this.formSubmit = false;
        this.hasCommentEditorContent = false;
        this.hasFileuploadContent = false;
    }

    /**
     * Event-listener that handles navigation related actions such as navigating 
     * away from the view or reloading the page, based on the current state of the form.
     */
    addWindowNavigationListener () {
      window.addEventListener('beforeunload', (event) => {
          if (this.formSubmit) {
              return;
          }
          if (this.hasCommentEditorContent || this.hasFileuploadContent) {
            const confirmed = window.confirm(this.windowChangeConfirmMessage);
            if (!confirmed) {
                event.preventDefault();
                event.returnValue = '';
            }
          }
      });
    }

    /**
     * Event-listener that stores whether the form is being submitted 
     * or not. This is to prevent the navigation warning prompt.
     */
    addFormSubmitListener () {
        document.getElementById('cradmin_legacy_createform')
            .addEventListener('submit', (event) => {
                this.formSubmit = true;
            });
    }

    /**
     * Event-listener that stores whether the comment-editor has 
     * any content or not.
     */
    addCommentEditorContentListener () {
        document.getElementById('id_devilry_comment_editor')
            .addEventListener('devilryCommentEditorHasContent', (event) => {
                this.hasCommentEditorContent = event.detail;
            }, false);
    }

    /**
     * Event-listener that stores whether file(s) has been uploaded 
     * or are being processed in any way.
     */
    addFileuploadContentListener () {
      document.getElementById('id_temporary_file_upload_component')
            .addEventListener('devilryFileuploadHasContent', (event) => {
                this.hasFileuploadContent = event.detail;
            }, false);
    }
}