import React from 'react'
import DropDownSearchFilter from './DropDownSearchFilter'
import * as gettext from 'ievv_jsbase/lib/gettext'
import AriaDescribedByTarget from '../../../components/AriaDescribedByTarget'

export default class AbstractMultiSelectDropDownSearchFilter extends DropDownSearchFilter {
  static get defaultProps () {
    return {
      ...super.defaultProps,
      selectedValueExtraAriaDescription: null,
      willReceiveSelectionEvents: true
    }
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClickDeselectItem = this.onClickDeselectItem.bind(this)
  }

  onClickClearButton () {
    this.props.childExposedApi.deselectAllItems()
    super.onClickClearButton()
  }

  onClickDeselectItem (selectedItemId, selectedItemData) {
    this.props.childExposedApi.deselectItem(selectedItemId)
    window.setTimeout(() => {
      this.getSearchInputRef().focus()
    }, 100)
  }

  onSelectItems (listItemIds) {
    window.setTimeout(() => {
      this.getSearchInputRef().focus()
    }, 100)
  }

  onDeselectItems (listItemIds) {
    window.setTimeout(() => {
      this.getSearchInputRef().focus()
    }, 100)
  }

  getSelectedLabelText (selectedItemId, selectedItemData) {
    throw new Error('getSelectedLabelText must be overridden by subclasses!')
  }

  renderSelectedLabel (selectedItemId, selectedItemData) {
    return this.getSelectedLabelText(selectedItemId, selectedItemData)
  }

  getSelectedValueExtraAriaDescribedByDomId (selectedItemId, selectedItemData) {
    return this.makeDomId('selectedValueExtraAriaDescribedBy')
  }

  getSelectedValueAriaLabel (selectedItemId, selectedItemData) {
    return gettext.interpolate(
      gettext.gettext('"%(selectedValue)s" selected. Click the button to remove it from your selection.'),
      {
        'selectedValue': this.getSelectedLabelText(selectedItemId, selectedItemData)
      },
      true)
  }

  renderSelectedValueExtraAriaDescribedBy (domId, selectedItemId, selectedItemData) {
    if (this.props.selectedValueExtraAriaDescription === null) {
      return null
    }
    return <AriaDescribedByTarget
      domId={domId}
      message={this.props.selectedValueExtraAriaDescription}
      key={'selectedValue extra aria-describedby'} />
  }

  getSelectedValueAriaDescribedByDomIds (extraDomId) {
    let domIds = [
      this.labelDomId
    ]
    if (this.props.selectedValueExtraAriaDescription !== null) {
      domIds.push(extraDomId)
    }
    return domIds
  }

  get selectedItemPreviewStyle () {
    return {
      maxWidth: '150px',
      overflow: 'hidden',
      textOverflow: 'ellipsis'
    }
  }

  renderSelectedItem (selectedItemId, selectedItemData) {
    const extraAriaDescribedByDomId = this.getSelectedValueExtraAriaDescribedByDomId(selectedItemId, selectedItemData)
    return [
      this.renderSelectedValueExtraAriaDescribedBy(extraAriaDescribedByDomId, selectedItemId, selectedItemData),
      <span
        className={'searchinput__selected'}
        key={`selected value ${selectedItemId}`}
      >
        <span
          className={'searchinput__selected_preview searchinput__selected_preview--with-deselect'}
          style={this.selectedItemPreviewStyle}
          title={this.getSelectedLabelText(selectedItemId, selectedItemData)}
        >
          {this.renderSelectedLabel(selectedItemId, selectedItemData)}
        </span>
        <button
          className={'searchinput__deselect'}
          type={'button'}
          onClick={() => { this.onClickDeselectItem(selectedItemId, selectedItemData) }}
          aria-label={this.getSelectedValueAriaLabel(selectedItemId, selectedItemData)}
          aria-describedby={this.getSelectedValueAriaDescribedByDomIds(extraAriaDescribedByDomId).join(' ')}
        >
          <span className='searchinput__deselect_icon cricon cricon--close cricon--color-light' />
        </button>
      </span>
    ]
  }

  renderSelectedItems () {
    let renderedItems = []
    for (let [selectedItemId, selectedItemData] of this.props.selectedListItemsMap) {
      renderedItems.push(this.renderSelectedItem(selectedItemId, selectedItemData))
    }
    return renderedItems
  }

  renderBodyContent () {
    return [
      ...this.renderSelectedItems(),
      this.renderSearchInput()
    ]
  }
}
