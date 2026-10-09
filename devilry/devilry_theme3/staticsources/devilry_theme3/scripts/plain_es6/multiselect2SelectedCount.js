const TARGET_CSS_SELECTOR = '.cradmin-legacy-multiselect2-target';
const SELECTED_ITEMS_CSS_SELECTOR = '.cradmin-legacy-multiselect2-target-selected-items';
const SELECTED_ITEM_CSS_CLASS = 'cradmin-legacy-multiselect2-target-selected-item';

/**
 * Renders the number of selected items in a cradmin_legacy multiselect2 target as ``(<count>)``.
 *
 * Must be placed within the ``.cradmin-legacy-multiselect2-target`` form. The selected items
 * are added and removed by the cradmin_legacy multiselect2 angularjs directives, so we observe
 * the selected items container and update the count whenever its children change.
 */
class DevilryMultiselect2SelectedCount extends HTMLElement {
    connectedCallback () {
        const selectedItemsElement = this._findSelectedItemsElement();
        if (!selectedItemsElement) {
            return;
        }
        this.observer = new MutationObserver(() => {
            this.renderCount(selectedItemsElement);
        });
        this.observer.observe(selectedItemsElement, {childList: true});
        this.renderCount(selectedItemsElement);
    }

    disconnectedCallback () {
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
    }

    _findSelectedItemsElement () {
        const targetElement = this.closest(TARGET_CSS_SELECTOR);
        if (!targetElement) {
            return null;
        }
        return targetElement.querySelector(SELECTED_ITEMS_CSS_SELECTOR);
    }

    _countSelectedItems (selectedItemsElement) {
        return Array.from(selectedItemsElement.children)
            .filter((element) => element.classList.contains(SELECTED_ITEM_CSS_CLASS))
            .length;
    }

    renderCount (selectedItemsElement) {
        this.textContent = `(${this._countSelectedItems(selectedItemsElement)})`;
    }
}

window.customElements.define('devilry-multiselect2-selected-count', DevilryMultiselect2SelectedCount);
