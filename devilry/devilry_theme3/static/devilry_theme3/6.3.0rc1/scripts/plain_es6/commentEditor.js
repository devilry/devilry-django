import { devilryParseDomString } from './webcomponent_utils.js';
import { getCookie } from './cookie.js';
import './latex_math.js';


const TOOLBAR_KEYBOARD_MAP = {
    'ctrl': false,      // CTRL (Windows)
    'Meta': false,      // CMD (macOS)
    'Enter': false,     // Enter
    'Shift': false,     // Shift
    'b': false,         // CTRL or CMD + b: bold
    'i': false,         // CTRL or CMD + i: italic
    'k': false,         // CTRL or CMD + k: link
    '7': false,         // CTRL or CMD + Shift + 7: Ordered list
    '8': false,         // CTRL or CMD + Shift + 8: Unordered list
};
const TOOLBAR_HEADING = 'heading';
const TOOLBAR_BOLD = 'bold';
const TOOLBAR_ITALIC = 'italic';
const TOOLBAR_LINK = 'link';
const TOOLBAR_CODE_INLINE = 'codeInline';
const TOOLBAR_CODE_BLOCK = 'codeBlock';
const TOOLBAR_UNORDERED_LIST = 'unorderedList';
const TOOLBAR_ORDERED_LIST = 'orderedList';
const TOOLBAR_IMAGE = 'image';
const ORDERED_LIST_REGEX = '^(\\s*)([0-9]*\\.\\s)';
const UNORDERED_LIST_REGEX = '^(\\s*)(\\*\\s)';

class DevilryCommentEditor extends HTMLElement {
    constructor() {
        super();

        this.attrLabelText = this.getAttribute('labelText');
        this.attrTextareaName = this.getAttribute('name');
        this.attrTextareaValue = this.getAttribute('value');
        this.attrTextareaPlaceholder = this.getAttribute('placeholder');
        this.attrHelpText = this.getAttribute('helpText');
        this.attrMarkdownGuideLinkUrl = this.getAttribute('markdownGuideLinkUrl');
        this.attrMarkdownGuideLinkText = this.getAttribute('markdownGuideLinkText');
        this.attrMarkdownPreviewConfig = JSON.parse(this.getAttribute('markdownPreviewConfig'));
        this.attrToolbarConfig = JSON.parse(this.getAttribute('toolbarConfig'));

        this.activeTab = 'write';
    }

    connectedCallback() {
        this.renderEditor();
        this.addToolbarOptionEventListeners();
        this.addToolbarKeyboardShortcutEvents();
        this.addTabEventListener();
    }

    get _elementId() {
        return `id_${this.attrTextareaName}`;
    }

    get _textArea() {
        return document.getElementById(`${this._elementId}`);
    }

    get _tooltipMetaKeyForPlatform() {
        return this._isMac ? 'Cmd' : 'Ctrl'
    }

    get _isMac() {
        return window.navigator.platform.toUpperCase().startsWith('MAC');
    }

    get _cursorLine() {
        const cursorStartIndex = this._textArea.value.substring(0, this._textArea.selectionStart).split('\n').length - 1;
        return this._textArea.value.split('\n')[cursorStartIndex];
    }

    get _newPreviewSection() {
        if (!this.attrMarkdownPreviewConfig.enabled) {
            return '';
        }
        return `
        <div id="${this._elementId}_comment_editor_preview_section" class="devilry-comment-editor-preview"></div>
        `;
    }

    get _buttonTab() {
        if (!this.attrMarkdownPreviewConfig.enabled) {
            return '';
        }
        return `
        <div class="tab">
            <button
                id="${this._elementId}_tab_button_write"
                class="tablinks active"
                type="button" disabled="true">
                    ${this.attrMarkdownPreviewConfig.editorActiveButtonText}
                </button>
            <button
                id="${this._elementId}_tab_button_preview"
                class="tablinks"
                type="button">
                ${this.attrMarkdownPreviewConfig.previewActiveButtonText}
                </button>
        </div>
        `
    }

    renderEditor() {
        const commentEditor = devilryParseDomString(`
            <div aria-live="polite">
                ${this._buttonTab}
                <div id="${this._elementId}_tab_content_write" class="tabcontent" style="display:block;">
                    <div id="${this._elementId}_comment_editor_section" class="devilry-comment-editor">
                        <div class="devilry-comment-editor-toolbar" aria-hidden="true">
                            <button
                                id="${this._elementId}_toolbar_option_heading"
                                type="button"
                                title="${this.attrToolbarConfig.heading.tooltip}"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-header cradmin-legacy-icon-font-sm"></span>
                            </button>
                            <button
                                id="${this._elementId}_toolbar_option_bold"
                                type="button"
                                title="${this.attrToolbarConfig.bold.tooltip}, ${this._tooltipMetaKeyForPlatform}+b"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-bold"></span>
                            </button>
                            <button
                                id="${this._elementId}_toolbar_option_italic"
                                type="button"
                                title="${this.attrToolbarConfig.italic.tooltip}, ${this._tooltipMetaKeyForPlatform}+i"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-italic"></span>
                            </button>
                            <button
                                id="${this._elementId}_toolbar_option_link"
                                type="button"
                                title="${this.attrToolbarConfig.link.tooltip}, ${this._tooltipMetaKeyForPlatform}+k"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-link"></span>
                            </button>
                            <button
                                id="${this._elementId}_toolbar_option_unordered_list"
                                type="button"
                                title="${this.attrToolbarConfig.unorderedList.tooltip}, ${this._tooltipMetaKeyForPlatform}+Shift+8"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-list-ul"></span>
                            </button>
                            <button
                                id="${this._elementId}_toolbar_option_code_block"
                                type="button"
                                title="${this.attrToolbarConfig.codeBlock.tooltip}"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-code"></span>
                            </button>
                            <button
                                id="${this._elementId}_toolbar_option_image"
                                type="button"
                                title="${this.attrToolbarConfig.image.tooltip}"
                                class="btn btn-default devilry-comment-editor-toolbar__option"
                            >
                                <span class="fa fa-image"></span>
                            </button>
                        </div>
                        <label for="${this._elementId}" class="screenreader-only" aria-hidden="true">${this.attrLabelText}</label>
                        <div class="devilry-comment-editor__textarea">
                            <textarea
                                id="${this._elementId}"
                                cols="40"
                                rows="10"
                                class="devilry-comment-editor-textarea devilry-comment-editor-textarea--real"
                                placeholder="${this.attrTextareaPlaceholder}"
                                name="${this.attrTextareaName}"
                                aria-describedby="${this._elementId}_help">${this.attrTextareaValue}</textarea>
                            <div id="${this._elementId}_textarea_content_copy" class="devilry-comment-editor-textarea devilry-comment-editor-textarea--copy" aria-hidden="true"></div>
                        </div>
                        <div class="devilry-comment-editor devilry-comment-editor__example-help">
                            <p id="${this._elementId}_help">
                                ${this.attrHelpText}
                                <a href="${this.attrMarkdownGuideLinkUrl}" target='_blank'>
                                    ${this.attrMarkdownGuideLinkText}
                                </a>
                            </p>
                        </div>
                    </div>
                </div>

                <div id="${this._elementId}_tab_content_preview" class="tabcontent" style="display:none;">
                    ${this._newPreviewSection}
                </div>
            <div>
        `);
        this.appendChild(commentEditor)
    }

    _fetchAndInjectRenderedMarkdown() {
        if (!this.attrMarkdownPreviewConfig.enabled) {
            return;
        }
        const previewArea = document.getElementById(`${this._elementId}_comment_editor_preview_section`);
        previewArea.innerHTML = `
        <span>
            <span class="fa fa-spinner fa-spin" aria-hidden="true"></span>
            <p class="text-muted">
                ${this.attrMarkdownPreviewConfig.previewApiFetchingMessage}
            </p>
        </span>
        `
        const textArea = this._textArea;
        fetch(this.attrMarkdownPreviewConfig.apiUrl, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ 'markdown_text': textArea.value })
        })
            .then(response => response.json())
            .then((responseData) => {
                previewArea.innerHTML = responseData['markdown_result'];
            })
            .catch((error) => {
                previewArea.innerHTML = this.attrMarkdownPreviewConfig.previewApiErrorMessage
            });
    }

    /**
     * Add event-listeners for write/preview "tab" buttons.
     */
    addTabEventListener() {
        if (!this.attrMarkdownPreviewConfig.enabled) {
            return;
        }
        const writeTabButton = document.getElementById(`${this._elementId}_tab_button_write`);
        const previewTabButton = document.getElementById(`${this._elementId}_tab_button_preview`);
        const writeTabContent = document.getElementById(`${this._elementId}_tab_content_write`);
        const previewTabContent = document.getElementById(`${this._elementId}_tab_content_preview`);

        // Active write tab content, deactive preview tab content.
        writeTabButton.addEventListener('click', () => {
            previewTabContent.style.display = 'none';
            previewTabButton.className = previewTabButton.className.replace(' active', '');
            previewTabButton.disabled = false;

            writeTabContent.style.display = 'block';
            writeTabButton.className += ' active';
            writeTabButton.disabled = true;

            this.activeTab = 'write';
            this._textArea.focus();
        });

        // Active preview tab content, deactive write tab content.
        previewTabButton.addEventListener('click', () => {
            writeTabContent.style.display = 'none';
            writeTabButton.className = previewTabButton.className.replace(' active', '');
            writeTabButton.disabled = false;

            previewTabContent.style.display = 'block';
            previewTabButton.className += ' active';
            previewTabButton.disabled = true;

            this.activeTab = 'preview';
            this._fetchAndInjectRenderedMarkdown();
        });
    }

    /**
     * Add event-listeners to toolbar buttons.
     */
    addToolbarOptionEventListeners() {
        document.getElementById(`${this._elementId}_toolbar_option_heading`)
            .addEventListener('click', () => {
                this.markdownActionHeading();
            }, false);
        document.getElementById(`${this._elementId}_toolbar_option_bold`)
            .addEventListener('click', () => {
                this.markdownActionBold();
            }, false);
        document.getElementById(`${this._elementId}_toolbar_option_italic`)
            .addEventListener('click', () => {
                this.markdownActionItalic();
            }, false);
        document.getElementById(`${this._elementId}_toolbar_option_link`)
            .addEventListener('click', () => {
                this.markdownActionLink();
            }, false);
        document.getElementById(`${this._elementId}_toolbar_option_code_block`)
            .addEventListener('click', () => {
                this.markdownActionCodeBlock();
            }, false);
        document.getElementById(`${this._elementId}_toolbar_option_unordered_list`)
            .addEventListener('click', () => {
                this.markdownActionUnorderedList();
            }, false);
        document.getElementById(`${this._elementId}_toolbar_option_image`)
            .addEventListener('click', () => {
                this.markdownActionImage();
            }, false);
    }

    /**
     * Add keyboard-shortcuts for toolbar actions.
     */
    addToolbarKeyboardShortcutEvents() {
        // Add key down event listener.
        document.onkeydown = (keyDownEvent) => {
            if (document.activeElement.id === `${this._elementId}`) {
                TOOLBAR_KEYBOARD_MAP[keyDownEvent.key] = true;

                // Handle MacOS vs everything else.
                let controlKey = 'Control';
                if (this._isMac) {
                    controlKey = 'Meta';
                }

                if (TOOLBAR_KEYBOARD_MAP[controlKey] && TOOLBAR_KEYBOARD_MAP['b']) {
                    this.markdownActionBold(keyDownEvent);
                } else if (TOOLBAR_KEYBOARD_MAP[controlKey] && TOOLBAR_KEYBOARD_MAP['i']) {
                    this.markdownActionItalic(keyDownEvent);
                } else if (TOOLBAR_KEYBOARD_MAP[controlKey] && TOOLBAR_KEYBOARD_MAP['k']) {
                    this.markdownActionLink(keyDownEvent);
                } else if (TOOLBAR_KEYBOARD_MAP[controlKey] && TOOLBAR_KEYBOARD_MAP['e']) {
                    this.markdownActionCodeInline(keyDownEvent);
                } else if (TOOLBAR_KEYBOARD_MAP[controlKey] && TOOLBAR_KEYBOARD_MAP['Shift'] && TOOLBAR_KEYBOARD_MAP['7']) {
                    this.markdownActionOrderedList();
                } else if (TOOLBAR_KEYBOARD_MAP[controlKey] && TOOLBAR_KEYBOARD_MAP['Shift'] && TOOLBAR_KEYBOARD_MAP['8']) {
                    this.markdownActionUnorderedList();
                } else if (TOOLBAR_KEYBOARD_MAP['Enter']) {
                    const cursorStartLine = this._cursorLine;
                    if (cursorStartLine.match(UNORDERED_LIST_REGEX)) {
                        this.markdownActionUnorderedList(keyDownEvent, false);
                    } else if (cursorStartLine.match(ORDERED_LIST_REGEX)) {
                        this.markdownActionOrderedList(keyDownEvent, false);
                    }
                }
            }
        };

        // Add key up event listener.
        document.onkeyup = (keyUpEvent) => {
            if (document.activeElement.id === `${this._elementId}`) {
                this.dispatchEvent(new CustomEvent('devilryCommentEditorHasContent', { detail: this._textArea.value ? true : false }));

                const textAreaContentCopy = document.getElementById(`${this._elementId}_textarea_content_copy`);
                textAreaContentCopy.innerHTML = `${this._textArea.value}X`;
                Object.keys(TOOLBAR_KEYBOARD_MAP).forEach(key => {
                    TOOLBAR_KEYBOARD_MAP[key] = false;
                });
            }
        };
    }

    _handleEventBehaviour(event = null, preventDefault = true) {
        if (event === null) {
            return;
        }
        if (preventDefault) {
            event.preventDefault();
        }
        event.stopPropagation();
    }

    markdownActionHeading(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_HEADING, '### ', '', this.attrToolbarConfig.heading.placeholderText);
    }

    markdownActionBold(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_BOLD, '**', '**', this.attrToolbarConfig.bold.placeholderText);
    }

    markdownActionItalic(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_ITALIC, '_', '_', this.attrToolbarConfig.italic.placeholderText);
    }

    markdownActionLink(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_LINK, '[', '](url)', this.attrToolbarConfig.link.placeholderText);
    }

    markdownActionCodeInline(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_CODE_INLINE, '`', '`', this.attrToolbarConfig.codeInline.placeholderText);
    }

    markdownActionCodeBlock(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_CODE_BLOCK, '```', '\n\n```', this.attrToolbarConfig.codeBlock.placeholderText);
    }

    markdownActionUnorderedList(event = null, preventDefault = true) {
        this._handleEventBehaviour(event, preventDefault);
        this.insertMarkdownListAtCursor(TOOLBAR_UNORDERED_LIST, event);
    }

    markdownActionOrderedList(event = null, preventDefault = true) {
        this._handleEventBehaviour(event, preventDefault);
        this.insertMarkdownListAtCursor(TOOLBAR_ORDERED_LIST, event);
    }

    markdownActionImage(event = null) {
        this._handleEventBehaviour(event, true);
        this.insertBasicMarkdownAtCursor(TOOLBAR_IMAGE, `![ ${this.attrToolbarConfig.image.placeholderTextDescription} ](`, ')', this.attrToolbarConfig.image.placeholderTextTitle);
    }

    /**
     * Inserts markdown-tag at cursor-position.
     * 
     * Inserts markdown-tag at cursor-position, by adding a opening and closing 
     * markdown-tag around the selected text (if any). When the markdown-tag is inserted, 
     * and the value for the text-area is updated, the cursor is placed at the end of the 
     * tagged text (including the closing markdown-tag).
     * 
     * @param {String} type         Type of markdown-tag.
     * @param {String} openingTag   The opening markdown-tag. E.g. for links where the full markdown tag is "[]()", the opening-tag whould be "(".
     * @param {String} closingTag   The closing markdown-tag. E.g. for links where the full markdown tag is "[]()", the closing-tag whould be "]()".
     * @param {String} placeholder  This is the placeholder text inserted between the opening and closing markdown tags if no text is selected.
     */
    insertBasicMarkdownAtCursor(type, openingTag, closingTag, placeholder) {
        if (![TOOLBAR_HEADING, TOOLBAR_BOLD, TOOLBAR_ITALIC, TOOLBAR_LINK, TOOLBAR_CODE_INLINE, TOOLBAR_CODE_BLOCK, TOOLBAR_IMAGE].includes(type)) {
            throw Error(`Type "${type}" not supported.`);
        }

        const textArea = this._textArea;
        const initialSelectionStart = textArea.selectionStart;
        const initialSelectionEnd = textArea.selectionEnd;

        let selectedText = textArea.value.substring(textArea.selectionStart, textArea.selectionEnd);

        if (!selectedText) {
            selectedText = placeholder || '';
        }
        const taggedText = openingTag + selectedText + closingTag
        textArea.value = textArea.value.substring(0, initialSelectionStart) + taggedText + textArea.value.substring(textArea.selectionEnd, textArea.value.length)

        // Places focus to the marked text as the selected range.
        textArea.focus()
        textArea.selectionStart = initialSelectionStart + openingTag.length;
        textArea.selectionEnd = initialSelectionEnd + openingTag.length;
    }

    /**
     * Insert ordered/unorderd list for selected text.
     * 
     * @param {String} type                 Type of markdown-tag.
     * @param {Object} enterKeyPressEvent   Enter key pressed event. Defaults to null. 
     *                                      If this is not null, then keypress is handled 
     *                                      by continuing the list on the current line.
     */
    insertMarkdownListAtCursor(type, enterKeyPressEvent = null) {
        if (![TOOLBAR_UNORDERED_LIST, TOOLBAR_ORDERED_LIST].includes(type)) {
            throw Error(`Type list-type "${type}" not supported.`);
        }

        const textArea = this._textArea;
        const cursorStartIndex = textArea.value.substring(0, textArea.selectionStart).split('\n').length - 1;
        const cursorEndIndex = textArea.value.substring(0, textArea.selectionEnd).split('\n').length - 1;
        const cursorStartEndIndexDiff = cursorEndIndex - cursorStartIndex;

        let textAreaLineArray = textArea.value.split('\n');
        let newTextAreaValue = '';
        let newSelectionStart = null;
        let newSelectionEnd = null;

        if (enterKeyPressEvent) {
            // Continue list on "Enter"-keypress.
            //
            // Continue the list by parsing the current line to find out 
            // if the current line is a numbered or a bulleted list. The 
            // next line will then be continued with the appropriate tag, 
            // where a numbered tag will be incremented based on the value 
            // of the current line. The array is then updated with the new 
            // numbered/bulleted line. If the cursor is in between text on 
            // the current line, the remainder of the text (from cursor position 
            // to the end of the line) will be cut, and added to the next line.
            //
            // The list will NOT be continued if the current line is an empty 
            // numbered or bulleted line. In this case, the will be "reset", and 
            // cursor is moved to the start of the line.
            //
            // The list will NOT be continued if a range of text is selected. In 
            // this case the default "Enter"-keypress behaviour will be applied 
            // instead.
            if (textArea.selectionStart !== textArea.selectionEnd) {
                return;
            }
            enterKeyPressEvent.preventDefault();

            const cursorLine = this._cursorLine;
            let listTag = '';

            // Set the tag to be used.
            // If the tag is empty, i.e has not been set, this means that 
            // the current list has no content after the tag. This will 
            // result in the line being reset.
            if (type === TOOLBAR_ORDERED_LIST) {
                const match = cursorLine.match(`${ORDERED_LIST_REGEX}(.+)`);
                if (match) {
                    listTag = match[1] + (parseInt(match[2]) + 1) + '. ';
                }
            } else {
                const match = cursorLine.match(`${UNORDERED_LIST_REGEX}(.+)`);
                if (match) {
                    listTag = match[1] + match[2];
                }
            }

            // This is the cursor position after the new line has been inserted with offset 
            // relative to where the cursor is currently at, and will be used set the cursor 
            // to the correct position when the new list-line has been added.
            let cursorPositionWithOffset = null;

            // Build the line array based on whether the new line to be inserted should continue 
            // the list or "reset" it.
            if (listTag) {

                // Cuts remainder of current line and adds it to 
                // the next line (if any).
                let totalLengthUntilCursorLine = 0;
                for (let i = 0; i < cursorStartIndex; i++) {
                    totalLengthUntilCursorLine += textAreaLineArray[i].length;
                }
                const indexWithinCursorLine = textArea.selectionStart - totalLengthUntilCursorLine - cursorStartIndex;

                // Build text area content with list item.
                textAreaLineArray = [
                    ...textAreaLineArray.slice(0, cursorStartIndex),
                    cursorLine.substring(0, indexWithinCursorLine),
                    `${listTag}${cursorLine.substring(indexWithinCursorLine)}`,
                    ...textAreaLineArray.slice(cursorStartIndex + 1)
                ];
                cursorPositionWithOffset = textArea.selectionStart + listTag.length + 1;
            } else {
                // Current list-line has no content, remove content and set 
                // cursor to line start.
                textAreaLineArray = [
                    ...textAreaLineArray.slice(0, cursorStartIndex),
                    listTag,
                    ...textAreaLineArray.slice(cursorStartIndex + 1)
                ];
                cursorPositionWithOffset = textArea.selectionStart - cursorLine.length;
            }

            // Set new cursor position.
            newSelectionStart = cursorPositionWithOffset;
            newSelectionEnd = cursorPositionWithOffset;
        } else {
            // Convert selected lines to list.
            //
            // The line(s) of the selected range of text will be converted to 
            // a list, where each line receives the appropriate list-tag (OL/UL).
            let markdownListTag = type === TOOLBAR_UNORDERED_LIST ? '* ' : '1. ';
            let orderedListCounter = 1;

            // Isolate the selected area, and add tags.
            const selectedAreaChunk = [];
            for (let i = cursorStartIndex; i <= cursorEndIndex; i++) {
                if (type === TOOLBAR_ORDERED_LIST) {
                    markdownListTag = `${orderedListCounter}. `;
                    orderedListCounter++;
                }
                selectedAreaChunk.push(
                    `${markdownListTag}${textAreaLineArray[i]}`
                );
            }

            // Update the array where the selected range has been tagged, and set cursor positions.
            textAreaLineArray = [
                ...textAreaLineArray.slice(0, cursorStartIndex),
                ...cursorStartIndex > 0 && textAreaLineArray[cursorStartIndex - 1].match('\.') ? [''] : [],
                ...selectedAreaChunk,
                ...cursorEndIndex < textAreaLineArray.length - 1 && textAreaLineArray[cursorEndIndex + 1].match('\.') ? [''] : [],
                ...textAreaLineArray.slice(cursorEndIndex + 1)
            ];
            if (cursorStartEndIndexDiff === 0) {
                newSelectionStart = textArea.selectionStart + markdownListTag.length;
                newSelectionEnd = textArea.selectionEnd + markdownListTag.length;
            } else {
                newSelectionStart = textArea.selectionStart + markdownListTag.length;
                newSelectionEnd = textArea.selectionEnd + (cursorStartEndIndexDiff * markdownListTag.length) + markdownListTag.length;
            }
        }

        // Rebuild the textarea value from the textAreaLineArray.
        // Append a newline character to each line except the last.
        const arrayLength = textAreaLineArray.length - 1;
        for (let i = 0; i < arrayLength; i++) {
            newTextAreaValue += textAreaLineArray[i] + '\n';
        }
        newTextAreaValue += textAreaLineArray[arrayLength];

        // Update textarea.
        textArea.value = newTextAreaValue;
        textArea.focus();
        if (newSelectionStart) {
            textArea.selectionStart = newSelectionStart;
        }
        if (newSelectionEnd) {
            textArea.selectionEnd = newSelectionEnd;
        }
    }
}

window.customElements.define('devilry-comment-editor', DevilryCommentEditor);