import React from 'react'
import PropTypes from 'prop-types'
import AbstractSelectedItems from './AbstractSelectedItems'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import BemUtilities from '../../../utilities/BemUtilities'

/**
 * Render selected items using the `blocklist` css component.
 *
 * See {@link BlockListRenderSelectedItems.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "BlockListRenderSelectedItems"
 * }
 *
 * @example <caption>Spec - custom attribute as the label</caption>
 * {
 *    "component": "BlockListRenderSelectedItems",
 *    "props": {
 *       "itemLabelAttribute": "name"
 *    }
 * }
 *
 * @example <caption>Spec - no BEM variants (render as block list)</caption>
 * {
 *    "component": "BlockListRenderSelectedItems",
 *    "props": {
 *       "bemVariants": []
 *    }
 * }
 */
export default class BlockListRenderSelectedItems extends AbstractSelectedItems {
  static get propTypes () {
    return Object.assign({}, {
      label: PropTypes.string,
      itemTitleAttribute: PropTypes.string.isRequired,
      itemDescriptionAttribute: PropTypes.string,
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
      itemTitleAttribute: 'title',
      itemDescriptionAttribute: '',
      bemVariants: ['tight']
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
    return 'blocklist'
  }

  get className () {
    return BemUtilities.addVariants(this.bemBlock, this.props.bemVariants)
  }

  get selectedItemClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'item')
  }

  get selectedItemContentClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'itemtitle')
  }

  get selectedItemIconBlockClassName () {
    return BemUtilities.buildBemElement(this.bemBlock, 'icon')
  }

  get selectedItemIconClassName () {
    return 'cricon cricon--close cricon--color-light'
  }

  getSelectedItemTitle (listItemData) {
    return listItemData[this.props.itemTitleAttribute]
  }

  getSelectedItemDescription (listItemData) {
    if (this.props.itemDescriptionAttribute === '') {
      return null
    }
    return listItemData[this.props.itemDescriptionAttribute]
  }

  renderSelectedItemTitle (listItemData) {
    return this.getSelectedItemTitle(listItemData)
  }

  renderSelectedItemDescription (listItemData) {
    let description = this.getSelectedItemDescription(listItemData)
    if (description !== null) {
      return <p className={'help-text'}>{description}</p>
    }
    return null
  }

  renderSelectedItemTitleDescription (listItemId, listItemData) {
    if (listItemData === null) {
      return null
    }
    return <div className={'blocklist__action-content'} key={`${listItemId} action-content title-description`}>
      {this.renderSelectedItemTitle(listItemData)}
      {this.renderSelectedItemDescription(listItemData)}
    </div>
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
    return [
      <div
        className="blocklist__action-sidebar"
        onClick={() => {this.onClick(listItemId)}}
        key={`${listItemId} action-sidebar-delete`}>
        <button className="blocklist__action-button" aria-label="Delete" type="button">
          <span className="cricon cricon--trash" aria-hidden="true" />
        </button>
      </div>,
      this.renderSelectedItemTitleDescription(listItemId, listItemData)
    ]
  }

  renderSelectedItem (listItemId, listItemData) {
    return <div
      tabIndex={0}
      key={listItemId}
      className={`${this.selectedItemClassName} blocklist__item--with-action-sidebar`}
      role='button'
      onFocus={this.onFocus}
      onBlur={this.onBlur}>
      {this.renderSelectedItemContent(listItemId, listItemData)}
    </div>
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
      <div className={this.className}>
        {this.renderSelectedItems()}
      </div>
    </div>
  }
}
