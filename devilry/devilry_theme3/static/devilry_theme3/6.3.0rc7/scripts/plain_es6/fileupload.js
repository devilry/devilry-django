import { devilryParseDomString } from './webcomponent_utils.js';
import { getCookie } from './cookie.js';


class DevilryTemporaryFileUploadQueueItem {
    constructor ({idPrefix, file, uploadApiUrl, i18n, onDeleteStart, onDeleteComplete}) {
        this.idPrefix = idPrefix;
        this.file = file;
        this.uploadApiUrl = uploadApiUrl;
        this.i18n = i18n;
        this.status = 'not-started';
        this.response = null;
        this.responseData = null;
        this.collectionId = null;
        this.temporaryFileData = null;
        this.onDeleteStart = onDeleteStart;
        this.onDeleteComplete = onDeleteComplete;
        this.domElement = devilryParseDomString(`
            <div class='devilry-fileupload-queue-item'>
                <div class='devilry-fileupload-iteminfo' aria-live='polite'>
                    <span class='devilry-fileupload-filestatus' id='${this.getDomId("filestatus")}'>
                        <span class='sr-only'>${this.i18n.uploadStatusLabel}</span>
                        <span id='${this.getDomId("filestatus_text")}'>${this.fileStatusLabel}</span>
                    </span>
                    <span class='devilry-fileupload-itemdetails' id='${this.getDomId("itemdetails")}'>
                        <span class='devilry-fileupload-filename'>${file.name}</span>
                        <span id='${this.getDomId("errormessage")}' class='devilry-fileupload-errormessage'>${this.errorMessage}</span>
                    </span>
                </div>
                <button type='button' class='btn btn--default devilry-fileupload-queue-removeitem'
                        id='${this.getDomId("removeitem")}'
                        aria-describedby='${this.getDomId("itemdetails")} ${this.getDomId("filestatus")}'>
                    <span class='fa fa-times' aria-hidden='true'></span>
                </button>
            </div>`);
    }

    getDomId (suffix = '') {
        if (suffix) {
            return `${this.idPrefix}_${suffix}`
        }
        return this.idPrefix;
    }

    addEventListeners () {
        document.getElementById(this.getDomId("removeitem")).addEventListener('click', (e) => {
            this.onRemoveItemButtonClick();
        });
    }

    onRemoveItemButtonClick () {
        if (this.status === 'upload-success' || this.status === 'delete-failed') {
            this.onDeleteStart(this);
            this.deleteFile();
        } else {
            this.onDeleteComplete(this);
        }
    }

    async deleteFile () {
        this.status = 'deleting';
        this.refreshDomItem();
        try {
            this.response = await fetch(this.uploadApiUrl, {
                method: "DELETE", 
                body: JSON.stringify({
                    'collectionid': this.collectionId,
                    'temporaryfileid': this.temporaryFileData.id
                }),
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            if (this.response.status === 200) {
                this.status = 'delete-success';
                this.onDeleteComplete(this);
            } else {
                this.status = 'delete-failed';
            }
        } catch (error) {
            console.error('FAILED TO DELETE FILE:', error);
            this.status = 'delete-failed';
        }
        if (this.status !== 'delete-success') {
            this.refreshDomItem();
            alert(this.i18n.deleteFileFailedMessage);
        }
    }

    async uploadFile (collectionId, onComplete) {
        this.status = 'uploading';
        let formData = new FormData();
        if (collectionId !== null) {
            formData.append('collectionid', collectionId);
        }
        formData.append('file', this.file);
        try {
            this.response = await fetch(this.uploadApiUrl, {
                method: "POST", 
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            if (this.response.status === 200) {
                this.status = 'upload-success';
            } else {
                this.status = 'upload-failed';
            }
            if (this.response.status === 200 || this.response.status === 400) {
                this.response.json()
                    .then((responseData) => {
                        this.responseData = responseData;
                        if (this.response.status === 200) {
                            this.collectionId = responseData.collectionid;
                            this.temporaryFileData = responseData.temporaryfiles[0];
                        }
                        onComplete(this);
                    })
                    .catch((error) => {
                        // It is very very strange if we get a 200 or 400 error that is not
                        // valid JSON, so we just crash.
                        throw error;
                    });
            } else {
                onComplete(this);
            }
        } catch (error) {
            console.error('FAILED:', error);
            this.status = 'upload-failed';
            onComplete(this);
        }
    }

    get fileStatusLabel () {
        if (this.status === 'upload-failed') {
            return this.i18n.uploadStatusFailed;
        } else if (this.status === 'upload-success') {
            return this.i18n.uploadStatusSuccess;
        } else if (this.status === 'deleting') {
            return this.i18n.uploadStatusDeleting;
        } else if (this.status === 'delete-failed') {
            return this.i18n.uploadStatusDeleteFailed;
        } else {
            return this.i18n.uploadStatusUploading;
        }
    }

    get removeItemLabel () {
        if (this.status === 'upload-failed') {
            return this.i18n.closeErrorLabel;
        } else {
            return this.i18n.removeFileLabel;
        }
    }

    get apiErrorMessages () {
        if (this.response === null || this.response.status !== 400) {
            return [];
        }
        let errorMessages = [];
        for (let [fieldname, errors] of Object.entries(this.responseData)) {
            for (let error of errors) {
                errorMessages.push(error.message);
            }
        }
        return errorMessages;
    }

    get errorMessage () {
        if (this.status !== 'upload-failed') {
            return '';
        }
        if (this.response !== null) {
            if (this.response.status === 400) {
                return this.apiErrorMessages.join(' ');
            } else if (this.response.status === 503) {
                return this.i18n.errorMessage503;
            }
        }
        return this.i18n.errorMessageUnknown;
    }

    get removeItemElement () {
        return document.getElementById(this.getDomId("removeitem"));
    }

    refreshDomItem () {
        this.domElement.classList.remove('devilry-fileupload-queue-item--upload-success');
        this.domElement.classList.remove('devilry-fileupload-queue-item--not-started');
        this.domElement.classList.remove('devilry-fileupload-queue-item--upload-failed');
        this.domElement.classList.remove('devilry-fileupload-queue-item--deleting');
        this.domElement.classList.remove('devilry-fileupload-queue-item--delete-failed');
        this.domElement.classList.remove('devilry-fileupload-queue-item--delete-success');
        this.domElement.classList.add(`devilry-fileupload-queue-item--${this.status}`);

        const fileStatusTextElement = document.getElementById(this.getDomId("filestatus_text"));
        const errorMessageElement = document.getElementById(this.getDomId("errormessage"));
        fileStatusTextElement.innerText = this.fileStatusLabel;
        this.removeItemElement.setAttribute('title', this.removeItemLabel);
        errorMessageElement.innerText = this.errorMessage;
    }
}

class DevilryTemporaryFileUpload extends HTMLElement {
    constructor () {
        super();
        this.idPrefix = this.getAttribute('idPrefix');
        this.hiddenFieldName = this.getAttribute('hiddenFieldName');
        this.labelDragDropHelp = this.getAttribute('labelDragDropHelp');
        this.uploadApiUrl = this.getAttribute('uploadApiUrl');
        this.labelUploadFilesButton = this.getAttribute('labelUploadFilesButton');
        this.screenReaderLabelUploadFilesButton = this.getAttribute('screenReaderLabelUploadFilesButton');
        this.screenReaderFilesQueuedMessage = this.getAttribute('screenReaderFilesQueuedMessage');
        this.screenReaderFilesQueueHowtoMessage = this.getAttribute('screenReaderFilesQueueHowtoMessage');
        this.labelInvalidFileType = this.getAttribute('labelInvalidFileType');
        this.uploadStatusUploading = this.getAttribute('uploadStatusUploading');
        this.uploadStatusSuccess = this.getAttribute('uploadStatusSuccess');
        this.uploadStatusDeleting = this.getAttribute('uploadStatusDeleting');
        this.uploadStatusDeleteFailed = this.getAttribute('uploadStatusDeleteFailed');
        this.uploadStatusFailed = this.getAttribute('uploadStatusFailed');
        this.uploadStatusLabel = this.getAttribute('uploadStatusLabel');
        this.closeErrorLabel = this.getAttribute('closeErrorLabel');
        this.removeFileLabel = this.getAttribute('removeFileLabel');
        this.maxFilenameLength = this.getAttribute('maxFilenameLength');
        this.maxFilenameLengthErrorMessage = this.getAttribute('maxFilenameLengthErrorMessage');
        this.errorMessage503 = this.getAttribute('errorMessage503');
        this.errorMessageUnknown = this.getAttribute('errorMessageUnknown');
        this.deleteFileFailedMessage = this.getAttribute('deleteFileFailedMessage');
        this.uploadQueue = [];
        this.collectionId = null;
        this.fileIndex = 1;
    }
    
    getDomId (suffix = '') {
        if (suffix) {
            return `${this.idPrefix}_${suffix}`
        }
        return this.idPrefix;
    }

    sendChangeEvent () {
        this.dispatchEvent(new CustomEvent('devilryFileuploadHasContent', {
            detail: this.hasUploadedFiles() || this.isUploading() || this.isDeleting()
        }));
    }

    hasUploadedFiles () {
        for (let queueItem of this.uploadQueue) {
            if (queueItem.status === 'upload-success') {
                return true;
            }
        }
        return false;
    }

    updateHiddenFormField () {
        if (this.collectionId !== null) {
            document.getElementById(this.getDomId('collection_id_field')).value = `${this.collectionId}`;
        }
    }

    _getFormElement (currentElement) {
        if (currentElement.tagName.toLowerCase() === 'form') {
            return currentElement;
        }
        return this._getFormElement(currentElement.parentNode);
    }

    getFormElement () {
        return this._getFormElement(this);
    }

    getFormSubmitButtonElements () {
        return Array.from(this.getFormElement().querySelectorAll('button[type=submit]'))
    }

    disableFormSubmitButton () {
        for (let button of this.getFormSubmitButtonElements()) {
            button.disabled = true;
        }    
    }

    enableFormSubmitButtonIfNotUploading () {
        if (!this.isUploading()) {
            for (let button of this.getFormSubmitButtonElements()) {
                button.disabled = false;
            }
        }
    }

    onQueueItemUploadComplete (queueItem) {
        queueItem.refreshDomItem();
        if (this.collectionId === null && queueItem.status == 'upload-success') {
            this.collectionId = queueItem.collectionId;
            // Upload the other files that have come while we uploaded the first
            for (let otherQueueItem of this.uploadQueue) {
                if (otherQueueItem.status === 'not-started') {
                    otherQueueItem.uploadFile(this.collectionId, () => {
                        this.onQueueItemUploadComplete(otherQueueItem);
                    })
                }
            }
        }
        this.updateHiddenFormField();
        this.enableFormSubmitButtonIfNotUploading();
        this.sendChangeEvent();
    }

    isUploading () {
        for (let queueItem of this.uploadQueue) {
            if (queueItem.status === 'uploading') {
                return true;
            }
        }
        return false;
    }

    isDeleting () {
        for (let queueItem of this.uploadQueue) {
            if (queueItem.status === 'deleting') {
                return true;
            }
        }
        return false;
    }

    uploadQueueItem (queueItem) {
        if (this.collectionId === null) {
            if (!this.isUploading()) {
                queueItem.status = 'uploading';
                queueItem.uploadFile(null, () => {
                    this.onQueueItemUploadComplete(queueItem);
                });
            }
            // If we do not have a collectionId, we only upload the first file to get
            // the collectionId. onQueueItemUploadComplete() makes sure the rest of the file 
            // upload queue is uploaded when we get the collectionId
        } else {
            queueItem.uploadFile(this.collectionId, () => {
                this.onQueueItemUploadComplete(queueItem);
            });
        }
        this.sendChangeEvent();
    }

    onDeleteQueueItemStart (queueItem) {
        this.disableFormSubmitButton();
        this.sendChangeEvent();
    }

    onDeleteQueueItemComplete (deletedQueueItem) {
        this.enableFormSubmitButtonIfNotUploading();
        const index = this.uploadQueue.indexOf(deletedQueueItem);
        if (index !== -1) {
            this.uploadQueue.splice(index, 1);
            deletedQueueItem.domElement.remove();
            this.updateHiddenFormField();
            if (this.uploadQueue.length === 0) {
                this.fileUploadButtonElement.focus();
            } else {
                let focusIndex = index - 1;
                if (this.uploadQueue.length > (index + 1)) {
                    focusIndex = index;
                }
                this.uploadQueue[focusIndex].removeItemElement.focus();
            }
        }
        this.sendChangeEvent();
    }

    addFileToUploadQueue (file) {
        this.disableFormSubmitButton();
        const queueItem = new DevilryTemporaryFileUploadQueueItem({
            idPrefix: `${this.getDomId(this.fileIndex)}`,
            file: file,
            uploadApiUrl: this.uploadApiUrl,
            collectionId: this.collectionId,
            onDeleteComplete: (queueItem) => {
                this.onDeleteQueueItemComplete(queueItem);
            },
            onDeleteStart: (queueItem) => {
                this.onDeleteQueueItemStart(queueItem);
            },
            i18n: {
                'uploadStatusUploading': this.uploadStatusUploading,
                'uploadStatusSuccess': this.uploadStatusSuccess,
                'uploadStatusFailed': this.uploadStatusFailed,
                'uploadStatusDeleting': this.uploadStatusDeleting,
                'uploadStatusDeleteFailed': this.uploadStatusDeleteFailed,
                'uploadStatusLabel': this.uploadStatusLabel,
                'closeErrorLabel': this.closeErrorLabel,
                'removeFileLabel': this.removeFileLabel,
                'maxFilenameLength': this.maxFilenameLength,
                'maxFilenameLengthErrorMessage': this.maxFilenameLengthErrorMessage,
                'errorMessage503': this.errorMessage503,
                'errorMessageUnknown': this.errorMessageUnknown,
                'deleteFileFailedMessage': this.deleteFileFailedMessage,
            }
        });
        this.fileIndex ++;
        this.uploadQueue.push(queueItem);
        const uploadQueueElement = document.getElementById(this.getDomId('uploadqueue'));
        uploadQueueElement.appendChild(queueItem.domElement);
        queueItem.addEventListeners();
        this.uploadQueueItem(queueItem);
    }

    onFileSelect (fileList) {
        let filenames = [];
        for (let file of fileList) {
            this.addFileToUploadQueue(file);
            filenames.push(file.name);
        }
        window.setTimeout(() => {
            const filenamesPretty = filenames.join(', ');
            const notifyElement = document.getElementById(this.getDomId('aria-notify'));
            notifyElement.innerText = `${this.screenReaderFilesQueuedMessage} ${filenamesPretty}. ${this.screenReaderFilesQueueHowtoMessage}`;
        }, 1000);
    }

    get fileUploadButtonElement () {
        return document.getElementById(this.getDomId('fileuploadbutton'));
    }

    connectedCallback () {
        this.setAttribute('class', 'devilry-fileupload');
        this.contentElement = devilryParseDomString(`
            <div class="devilry-fileupload-content">
                <div class='devilry-fileupload-dropbox' aria-hidden='true' id='${this.getDomId('dropbox')}'>
                    <div class='devilry-fileupload-dropbox-text'>
                        ${this.labelDragDropHelp}
                    </div>
                    <div class='devilry-fileupload-dropbox-invalid-filetype-errormessage' style='display: none;'>
                        ${this.labelInvalidFileType}
                    </div>
                </div>
                <p class='devilry-fileupload-fileselect-wrapper'>
                    <label for='${this.getDomId('fileinput')}' class='devilry-fileupload-fileselect-label'>
                        <button type='button'
                                id='${this.getDomId('fileuploadbutton')}'
                                class='btn btn-xs btn-default devilry-fileupload-fileselect-button'
                                aria-label='${this.screenReaderLabelUploadFilesButton}'>
                            <span aria-hidden="true">
                                ${this.labelUploadFilesButton}
                            </span>
                        </button>
                    </label>
                    <input
                        id="${this.getDomId('fileinput')}"
                        type="file" multiple="multiple"
                        class='devilry-fileupload-fileselect-input'>
                </p>
                <div id='${this.getDomId('aria-notify')}' class='sr-only' aria-live='assertive'></div>
                <div id='${this.getDomId('uploadqueue')}' class='devilry-fileupload-queue'></div>
                <input id='${this.getDomId('collection_id_field')}' type='hidden' name='${this.hiddenFieldName}' value='' />
            </div>
        `);
        this.appendChild(this.contentElement);
        document.getElementById(this.getDomId('fileinput')).addEventListener('change', (e) => {
            this.onFileSelect(e.target.files);
        });
        this.fileUploadButtonElement.addEventListener('click', (e) => {
            document.getElementById(this.getDomId('fileinput')).click();
        });

        const dropbox = document.getElementById(this.getDomId('dropbox'));
        dropbox.addEventListener('dragenter', (e) => {
            e.stopPropagation();
            e.preventDefault();
            dropbox.classList.add('devilry-fileupload-dropbox-dragover');
        }, false);
        dropbox.addEventListener('dragover', (e) => {
            e.stopPropagation();
            e.preventDefault();
            dropbox.classList.add('devilry-fileupload-dropbox-dragover');
        }, false);
        dropbox.addEventListener('dragleave', (e) => {
            e.stopPropagation();
            e.preventDefault();
            dropbox.classList.remove('devilry-fileupload-dropbox-dragover');
        }, false);
        dropbox.addEventListener('drop', (e) => {
            e.stopPropagation();
            e.preventDefault();
            dropbox.classList.remove('devilry-fileupload-dropbox-dragover');
            this.onFileSelect(e.dataTransfer.files);
        }, false);
    }
}

window.customElements.define('devilry-temporary-file-upload', DevilryTemporaryFileUpload);

// Prevent default drag and drop to show file in current browser window behavior.
window.addEventListener("dragover", function(e) {
    e.preventDefault()
    }, false);
    window.addEventListener("drop", function(e) {
    e.preventDefault()
    }, false);
  