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

        console.log(`${this.attrAssignmentGroupId} - ${this.attrAssignStatus}`)
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
            return 'ERROR';
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

    _setUpdating (buttonElement) {
        this.attrAssignStatus = 'updating';
        buttonElement.innerText = this._buttonText;
        this._updateCssClass(buttonElement, 'examiner-selfassign-button--updating');
    }

    _performAssignUnassignAction (buttonElement, action, onSuccessCallback, onErrorCallback) {
        // Set updating state.
        this._setUpdating(buttonElement)

        // Perform API call.
        fetch(this.attrSelfAssignApiUrl, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
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

    _setError (buttonElement) {
        this.attrAssignStatus = 'error';
        buttonElement.innerText = this._buttonText;
    }

    addEventListeners () {
        const buttonElement = document.getElementById(this._elementId);
        buttonElement.addEventListener('click', () => {
            if (this.attrAssignStatus === 'updating') {
                return;
            }
            if (this.attrAssignStatus === 'assigned') {
                this._performAssignUnassignAction(
                    buttonElement,
                    ACTION_TYPE_ASSIGN,
                    () => {this._setUnassigned(buttonElement);},
                    () => {this._setError(buttonElement);}
                );
            } else if (this.attrAssignStatus === 'unassigned') {
                this._performAssignUnassignAction(
                    buttonElement,
                    ACTION_TYPE_UNASSIGN,
                    () => {this._setAssigned(buttonElement);},
                    () => {this._setError(buttonElement);}
                );
            } else {
                console.error(`ERROR ${this.attrAssignStatus}`);
            }
        });
    }

    renderButton () {
        console.log('Render button');
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