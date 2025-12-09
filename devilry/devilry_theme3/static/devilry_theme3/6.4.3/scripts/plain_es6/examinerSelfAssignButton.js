import { devilryParseDomString } from './webcomponent_utils.js';
import { getCookie } from './cookie.js';


const ACTION_TYPE_ASSIGN = 'ASSIGN';
const ACTION_TYPE_UNASSIGN = 'UNASSIGN';

class DevilryExaminerSelfAssignButton extends HTMLElement {
    constructor () {
        super();

        this.attrSelfAssignApiUrl = this.getAttribute('selfAssignApiUrl');
        this.attrAssignmentGroupId = this.getAttribute('assignmenGroupId');
        this.attrAssignStatus = this.getAttribute('assignStatus');
        this.attrAssignText = this.getAttribute('assignText');
        this.attrUnassignText = this.getAttribute('unassignText');
        this.attrUpdatingText = this.getAttribute('updatingText');
        this.attrAssignProgressText = this.getAttribute('assignProgressText');
        this.attrUnassignProgressText = this.getAttribute('unassignProgressText');
        this.attrUnavailableText = this.getAttribute('unavailableText');
    }

    connectedCallback () {
        this.renderButton();
        this.addEventListeners();
    }

    get _elementId () {
        return `id-devilry-examiner-selfassign-button-${this.attrAssignmentGroupId}`;
    }

    get _buttonText () {
        if (this.attrAssignStatus === 'assigned') {
            return this.attrUnassignText;
        } else if (this.attrAssignStatus === 'unassigned') {
            return this.attrAssignText;
        } else if (this.attrAssignStatus === 'updating') {
            return this.attrUpdatingText;
        } else {
            return this.attrUnavailableText;
        }
    }

    _updateCssClass (buttonElement, cssClassToSet) {
        buttonElement.classList.forEach(cssClass => {
            if (cssClass.startsWith('examiner-selfassign-button--')) {
                buttonElement.classList.remove(cssClass);
            }
        });
        buttonElement.classList.add(cssClassToSet);
    }

    _setUpdating (buttonElement, action) {
        this.attrAssignStatus = 'updating';
        if (action === ACTION_TYPE_ASSIGN) {
            buttonElement.innerText = this.attrAssignProgressText;
        } else {
            buttonElement.innerText = this.attrUnassignProgressText;
        }
        this._updateCssClass(buttonElement, 'examiner-selfassign-button--updating');
    }

    _performAssignUnassignAction (buttonElement, action, onSuccessCallback, onErrorCallback) {
        // Set updating state.
        this._setUpdating(buttonElement, action)

        // Perform API call.
        fetch(this.attrSelfAssignApiUrl, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'group_id': this.attrAssignmentGroupId,
                'action': action
            })
        })
        .then((response) => {
            if (response.status !== 200) {
                throw Error();
            }
            return response.json();
        })
        .then((responseData) => {
            onSuccessCallback();
        })
        .catch((error) => {
            onErrorCallback();
        });
    }

    _setAssigned (buttonElement) {
        this.attrAssignStatus = 'assigned';
        buttonElement.innerText = this._buttonText;
        this._updateCssClass(buttonElement, 'examiner-selfassign-button--assigned');
    }

    _setUnassigned (buttonElement) {
        this.attrAssignStatus = 'unassigned';
        buttonElement.innerText = this._buttonText;
        this._updateCssClass(buttonElement, 'examiner-selfassign-button--unassigned');
    }

    _setUnavailable (buttonElement) {
        this.attrAssignStatus = 'unavailable';
        buttonElement.innerText = this._buttonText;
    }

    addEventListeners () {
        const buttonElement = document.getElementById(this._elementId);
        buttonElement.addEventListener('click', () => {
            if (this.attrAssignStatus === 'assigned') {
                this._performAssignUnassignAction(
                    buttonElement,
                    ACTION_TYPE_UNASSIGN,
                    () => {this._setUnassigned(buttonElement);},
                    () => {this._setUnavailable(buttonElement);}
                );
            } else if (this.attrAssignStatus === 'unassigned') {
                this._performAssignUnassignAction(
                    buttonElement,
                    ACTION_TYPE_ASSIGN,
                    () => {this._setAssigned(buttonElement);},
                    () => {this._setUnavailable(buttonElement);}
                );
            }
        });
    }

    renderButton () {
        const selfAssignButton = devilryParseDomString(`
            <button
                type="button"
                class="btn btn-default examiner-selfassign-button--unassigned"
                id="${this._elementId}">
                ${this._buttonText}
            </button>
        `);
        this.appendChild(selfAssignButton);
    }
}

window.customElements.define('devilry-examiner-selfassign-button', DevilryExaminerSelfAssignButton);