export class DevilryCommentEditorHasContent {
    constructor (windowChangeConfirmMessage) {
        this.windowChangeConfirmMessage = windowChangeConfirmMessage;

        this.addWindowNavigationListener();
        this.addCommentEditorContentListener();
        this.addFileuploadContentListener();

        this.hasCommentEditorContent = false;
        this.hasFileuploadContent = false;
    }

    addWindowNavigationListener () {
      window.addEventListener('beforeunload', (event) => {
          if (this.hasCommentEditorContent || this.hasFileuploadContent) {
            const confirmed = window.confirm(this.windowChangeConfirmMessage);
            if (!confirmed) {
                event.preventDefault();
                event.returnValue = '';
            }
          }
      });
    }

    addCommentEditorContentListener () {
        document.getElementById('id_devilry_comment_editor')
            .addEventListener('devilryCommentEditorHasContent', (event) => {
                this.hasCommentEditorContent = event.detail;
            }, false);
    }

    addFileuploadContentListener () {
      document.getElementById('id_temporary_file_upload_component')
            .addEventListener('devilryFileuploadHasContent', (event) => {
                this.hasFileuploadContent = event.detail;
            }, false);
    }
}