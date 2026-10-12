import React from 'react'
import DropDownSearchFilter from './DropDownSearchFilter'
import * as gettext from 'ievv_jsbase/lib/gettext'
import AriaDescribedByTarget from '../../../components/AriaDescribedByTarget'

export default class AbstractSingleSelectDropDownSearchFilter extends DropDownSearchFilter {
  static get defaultProps () {
    return {
      ...super.defaultProps,
      selectedValueExtraAriaDescription: null,
      willReceiveSelectionEvents: true
    }
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClickSelectedItemBody = this.onClickSelectedItemBody.bind(this)
  }

  onClickClearButton () {
    this.props.childExposedApi.deselectAllItems()
    super.onClickClearButton()
  }

  onClickSelectedItemBody () {
    this.onClickClearButton()
  }

  onSelectItems (listItemIds) {
    window.setTimeout(() => {
      if (this._selectedItemButton) {
        this._selectedItemButton.focus()
      }
    }, 100)
  }

  onDeselectItems (listItemIds) {
    window.setTimeout(() => {
      this.getSearchInputRef().focus()
    }, 100)
  }

  getSelectedLabelText () {
    throw new Error('getSelectedLabelText must be overridden by subclasses!')
  }

  renderSelectedLabel () {
    return this.getSelectedLabelText()
  }

  get selectedValueExtraAriaDescribedByDomId () {
    return this.makeDomId('selectedValueExtraAriaDescribedBy')
  }

  get selectedItemKey () {
    if (this.props.selectedListItemsMap.size === 0) {
      return null
    }
    return this.props.selectedListItemsMap.keys().next().value
  }

  get selectedItemValue () {
    if (this.props.selectedListItemsMap.size === 0) {
      return null
    }
    return this.props.selectedListItemsMap.get(this.selectedItemKey)
  }

  get selectedValueAriaLabel () {
    return gettext.interpolate(
      gettext.gettext('"%(selectedValue)s" selected. Hit the enter button to change your selection.'),
      {
        'selectedValue': this.getSelectedLabelText()
      },
      true)
  }

  renderSelectedValueExtraAriaDescribedBy () {
    if (this.props.selectedValueExtraAriaDescription === null) {
      return null
    }
    return <AriaDescribedByTarget
      domId={this.selectedValueExtraAriaDescribedByDomId}
      message={this.props.selectedValueExtraAriaDescription}
      key={'selectedValue extra aria-describedby'} />
  }

  get selectedValueAriaDescribedByDomIds () {
    let domIds = [
      this.labelDomId
    ]
    if (this.props.selectedValueExtraAriaDescription !== null) {
      domIds.push(this.selectedValueExtraAriaDescribedByDomId)
    }
    return domIds
  }

  renderSelectedValue (extraProps) {
    return [
      this.renderSelectedValueExtraAriaDescribedBy(),
      <button
        className={'searchinput__selected searchinput__selected--single'}
        type={'button'}
        key={'selected value'}
        onClick={this.onClickSelectedItemBody}
        aria-label={this.selectedValueAriaLabel}
        aria-describedby={this.selectedValueAriaDescribedByDomIds.join(' ')}
        ref={(input) => { this._selectedItemButton = input }}
        {...extraProps}
      >
        <span className={'searchinput__selected_preview'}>
          {this.renderSelectedLabel()}
        </span>
      </button>
    ]
  }

  renderBodyContent () {
    const noneStyle = {
      style: {
        display: 'none'
      }
    }

    if (this.props.selectedListItemsMap.size === 0) {
      return [
        this.renderSearchInput(),
        ...this.renderSelectedValue(noneStyle)
      ]
    }
    return [
      this.renderSearchInput(noneStyle),
      ...this.renderSelectedValue()
    ]
  }
}
