import React from 'react'
import PropTypes from 'prop-types'
import AbstractSelectedItems from './AbstractSelectedItems'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import BemUtilities from '../../../utilities/BemUtilities'

/**
 * Render selected items using the `selectable-list` css component.
 *
 * See {@link SelectableListRenderSelectedItems.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "SelectableListRenderSelectedItems"
 * }
 *
 * @example <caption>Spec - custom attribute as the label</caption>
 * {
 *    "component": "SelectableListRenderSelectedItems",
 *    "props": {
 *       "itemLabelAttribute": "name"
 *    }
 * }
 *
 * @example <caption>Spec - no BEM variants (render as block list)</caption>
 * {
 *    "component": "SelectableListRenderSelectedItems",
 *    "props": {
 *       "bemVariants": []
 *    }
 * }
 */
export default class SelectableListRenderSelectedItems extends AbstractSelectedItems {
  static get propTypes () {
    return Object.assign({}, {
      label: PropTypes.string,
      itemLabelAttribute: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired,
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractSelectedItems.defaultProps}.
   *
   * @return {Object}
   * @property {string} itemLabelAttribute The list item data attribute
   *    to use as the label of selected items.
   *    This is required, and defaults to `title`.
   *    **Can be used in spec**.
   * @property {[string]} bemVariants BEM variants for the selectable-list.
   *    **Can be used in spec**.
   */
  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      label: window.gettext('Selected items:'),
      itemLabelAttribute: 'title',
      bemVariants: ['inline', 'nomargin']
    })
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClick = this.onClick.bind(this)
  }

  onClick (listItemId) {
    this.props.childExposedApi.deselectItem(listItemId)
  }

  get wrapperClassName () {
    return 'paragraph'
  }

  get bemBlock () {
    return 'selectable-list'
  }

  get className () {
    return BemUtilities.addVariants(this.bemBlock, this.props.bemVariants)
  }

  get selectedItemClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'item', ['selected'])
  }

  get selectedItemContentClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'itemcontent')
  }

  get selectedItemIconBlockClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'icon')
  }

  get selectedItemIconClassName () {
    return 'cricon cricon--close cricon--color-light'
  }

  getSelectedItemLabel (listItemData) {
    return listItemData[this.props.itemLabelAttribute]
  }

  renderSelectedItemIcon (listItemId, listItemData) {
    return <i className={this.selectedItemIconClassName} />
  }

  renderSelectedItemIconBlock (listItemId, listItemData) {
    return <div className={this.selectedItemIconBlockClassName}>
      {this.renderSelectedItemIcon(listItemId, listItemData)}
    </div>
  }

  renderSelectedItemContent (listItemId, listItemData) {
    if (listItemData === null) {
      return null
    }
    return <div className={this.selectedItemContentClassName}>
      {this.getSelectedItemLabel(listItemData)}
    </div>
  }

  renderSelectedItem (listItemId, listItemData) {
    return <li
      tabIndex={0}
      key={listItemId}
      className={this.selectedItemClassName}
      role='button'
      onClick={() => { this.onClick(listItemId) }}
      onFocus={this.onFocus}
      onBlur={this.onBlur}>
      {this.renderSelectedItemContent(listItemId, listItemData)}
      {this.renderSelectedItemIconBlock(listItemId, listItemData)}
    </li>
  }

  renderSelectedItems () {
    const renderedHiddenFields = []
    for (let [listItemId, listItemData] of this.props.selectedListItemsMap) {
      renderedHiddenFields.push(this.renderSelectedItem(
        listItemId, listItemData))
    }
    return renderedHiddenFields
  }

  renderLabel () {
    return this.props.label
  }

  render () {
    if (this.props.selectedListItemsMap.size === 0) {
      return null
    }
    return <div className={this.wrapperClassName}>
      {this.renderLabel()}
      <ul className={this.className}>
        {this.renderSelectedItems()}
      </ul>
    </div>
  }
}
