import { devilryParseDomString } from './webcomponent_utils.js';
import { getCookie } from './cookie.js';


class DevilryTemporaryFileUploadQueueItem {
    constructor ({idPrefix, file, uploadApiUrl, i18n}) {
        this.idPrefix = idPrefix;
        this.file = file;
        this.uploadApiUrl = uploadApiUrl;
        this.i18n = i18n;
        this.status = 'not-started';
        this.response = null;
        this.responseData = null;
        this.domElement = devilryParseDomString(`
            <div class='devilry-fileupload-queue-item'>
                <div class='devilry-fileupload-iteminfo'>
                    <span class='devilry-fileupload-filestatus' id='${this.getDomId("filestatus")}'>
                        <span class='sr-only'>${this.i18n.uploadStatusLabel}</span>
                        <span id='${this.getDomId("filestatus_text")}'>${this.fileStatusLabel}</span>
                    </span>
                    <span class='devilry-fileupload-itemdetails' id='${this.getDomId("itemdetails")}'>
                        <span class='devilry-fileupload-filename'>${file.name}</span>
                        <span id='${this.getDomId("errormessage")}' class='devilry-fileupload-errormessage'>${this.errorMessage}</span>
                    </span>
                </div>
                <button type='button' class='btn btn--default devilry-fileupload-queue-removeitem' id='${this.getDomId("removeitem")}'
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
            console.log('RESPONSE:', this.response);
            if (this.response.status === 200) {
                this.status = 'success';
            } else {
                this.status = 'failed';
            }
            if (this.response.status === 200 || this.response.status === 400) {
                this.response.json()
                    .then((responseData) => {
                        console.log('responseData:', responseData);
                        this.responseData = responseData;
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
            this.status = 'failed';
            onComplete(this);
        }
    }

    get fileStatusLabel () {
        if (this.status === 'failed') {
            return this.i18n.uploadStatusFailed;
        } else if (this.status === 'success') {
            return this.i18n.uploadStatusSuccess;
        } else {
            return this.i18n.uploadStatusUploading;
        }
    }

    get removeItemLabel () {
        if (this.status === 'failed') {
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
            console.log(fieldname, errors);
            for (let error of errors) {
                errorMessages.push(error.message);
            }
        }
        console.log(errorMessages);
        return errorMessages;
    }

    get errorMessage () {
        if (this.status !== 'failed') {
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

    refreshDomItem () {
        console.log('REFRESH:', this);
        this.domElement.classList.remove('devilry-fileupload-queue-item--success');
        this.domElement.classList.remove('devilry-fileupload-queue-item--not-started');
        this.domElement.classList.remove('devilry-fileupload-queue-item--failed');
        this.domElement.classList.add(`devilry-fileupload-queue-item--${this.status}`);

        const fileStatusTextElement = document.getElementById(this.getDomId("filestatus_text"));
        const removeItemElement = document.getElementById(this.getDomId("removeitem"));
        const errorMessageElement = document.getElementById(this.getDomId("errormessage"));
        fileStatusTextElement.innerText = this.fileStatusLabel;
        removeItemElement.setAttribute('title', this.removeItemLabel);
        errorMessageElement.innerText = this.errorMessage;
    }
}

class DevilryTemporaryFileUpload extends HTMLElement {
    constructor () {
        super();
        this.idPrefix = this.getAttribute('idPrefix');
        this.labelDragDropHelp = this.getAttribute('labelDragDropHelp');
        this.uploadApiUrl = this.getAttribute('uploadApiUrl');
        this.labelUploadFilesButton = this.getAttribute('labelUploadFilesButton');
        this.screenReaderLabelUploadFilesButton = this.getAttribute('screenReaderLabelUploadFilesButton');
        this.screenReaderFilesQueuedMessage = this.getAttribute('screenReaderFilesQueuedMessage');
        this.screenReaderFilesQueueHowtoMessage = this.getAttribute('screenReaderFilesQueueHowtoMessage');
        this.labelInvalidFileType = this.getAttribute('labelInvalidFileType');
        this.uploadStatusUploading = this.getAttribute('uploadStatusUploading');
        this.uploadStatusSuccess = this.getAttribute('uploadStatusSuccess');
        this.uploadStatusFailed = this.getAttribute('uploadStatusFailed');
        this.uploadStatusLabel = this.getAttribute('uploadStatusLabel');
        this.closeErrorLabel = this.getAttribute('closeErrorLabel');
        this.removeFileLabel = this.getAttribute('removeFileLabel');
        this.maxFilenameLength = this.getAttribute('maxFilenameLength');
        this.maxFilenameLengthErrorMessage = this.getAttribute('maxFilenameLengthErrorMessage');
        this.errorMessage503 = this.getAttribute('errorMessage503');
        this.errorMessageUnknown = this.getAttribute('errorMessageUnknown');
        this.uploadQueue = [];
        this.collectionId = null;
        this.fileIndex = 0;
    }
    
    getDomId (suffix = '') {
        if (suffix) {
            return `${this.idPrefix}_${suffix}`
        }
        return this.idPrefix;
    }

    onQueueItemUploadComplete (queueItem, isFirstQueueItem) {
        console.log('upload complete:', queueItem);
        queueItem.refreshDomItem();
        if (isFirstQueueItem && this.collectionId === null) {
            console.log('FIRST upload complete:', queueItem);
            this.collectionId = queueItem.responseData.collectionid;
            // Upload the other files that have come while we uploaded the first
            for (let otherQueueItem of this.uploadQueue) {
                if (otherQueueItem.status === 'not-started') {
                    otherQueueItem.uploadFile(this.collectionId, () => {
                        this.onQueueItemUploadComplete(otherQueueItem, false);
                    })
                }
            }
        }
    }

    uploadQueueItem (queueItem, isFirstQueueItem) {
        if (this.collectionId === null) {
            if (isFirstQueueItem) {
                queueItem.uploadFile(null, () => {
                    this.onQueueItemUploadComplete(queueItem, true);
                });
            }
            // If we do not have a collectionId, we only upload the first file to get
            // the collectionId. onQueueItemUploadComplete() makes sure the rest of the file 
            // upload queue is uploaded when we get the collectionId
        } else {
            queueItem.uploadFile(this.collectionId, () => {
                this.onQueueItemUploadComplete(queueItem, false);
            });
        }
    }

    addFileToUploadQueue (file) {
        const queueItem = new DevilryTemporaryFileUploadQueueItem({
            idPrefix: `${this.getDomId(this.fileIndex)}`,
            file: file,
            uploadApiUrl: this.uploadApiUrl,
            collectionId: this.collectionId,
            i18n: {
                'uploadStatusUploading': this.uploadStatusUploading,
                'uploadStatusSuccess': this.uploadStatusSuccess,
                'uploadStatusFailed': this.uploadStatusFailed,
                'uploadStatusLabel': this.uploadStatusLabel,
                'closeErrorLabel': this.closeErrorLabel,
                'removeFileLabel': this.removeFileLabel,
                'maxFilenameLength': this.maxFilenameLength,
                'maxFilenameLengthErrorMessage': this.maxFilenameLengthErrorMessage,
                'errorMessage503': this.errorMessage503,
                'errorMessageUnknown': this.errorMessageUnknown,
            }
        });
        this.fileIndex ++;
        this.uploadQueue.push(queueItem);
        const isFirstQueueItem = this.uploadQueue.length === 1;
        const uploadQueueElement = document.getElementById(this.getDomId('uploadqueue'));
        uploadQueueElement.appendChild(queueItem.domElement);
        this.uploadQueueItem(queueItem, isFirstQueueItem);
    }

    onFileSelect (fileList) {
        console.log(fileList);
        let filenames = [];
        for (let file of fileList) {
            this.addFileToUploadQueue(file);
        }
        window.setTimeout(() => {
            const filenamesPretty = filenames.join(', ');
            const notifyElement = document.getElementById(this.getDomId('aria-notify'));
            notifyElement.innerText = `${this.screenReaderFilesQueuedMessage} ${filenamesPretty}. ${this.screenReaderFilesQueueHowtoMessage}`;
        }, 1000);
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
            </div>
        `);
        this.appendChild(this.contentElement);
        document.getElementById(this.getDomId('fileinput')).addEventListener('change', (e) => {
            this.onFileSelect(e.target.files);
        });
        document.getElementById(this.getDomId('fileuploadbutton')).addEventListener('click', (e) => {
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
  