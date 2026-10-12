import React from 'react'
import PropTypes from 'prop-types'
import 'ievv_jsbase/lib/utils/i18nFallbacks'
import BlockListRenderSelectedItems from './BlockListRenderSelectedItems'


export default class BlockListRenderSortableSelectedItems extends BlockListRenderSelectedItems {
  static get propTypes () {
    return Object.assign({}, super.propTypes, {
      inlineMoveIcons: PropTypes.bool
    })
  }

  static get defaultProps () {
    return Object.assign({}, super.defaultProps, {
      inlineMoveIcons: false
    })
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onClickMoveUp = this.onClickMoveUp.bind(this)
    this.onClickMoveDown = this.onClickMoveDown.bind(this)
  }

  onClickMoveUp (listItemId) {
    this.props.childExposedApi.selectedItemMoveUp(listItemId)
  }

  onClickMoveDown (listItemId) {
    this.props.childExposedApi.selectedItemMoveDown(listItemId)
  }

  renderSelectedItemMoveUp (listItemId, withActionSidebar=true) {
    if (this.props.childExposedApi.selectedItemIsFirst(listItemId)) {
      return null
    }
    const button = <button
      type={"button"}
      className="blocklist__action-button"
      aria-label="Move up"
      onClick={() => {this.onClickMoveUp(listItemId)}}>
        <span className="cricon cricon--chevron-up" aria-hidden="true" />
    </button>

    if (withActionSidebar) {
      return <div className="blocklist__action-sidebar" key={`${listItemId} sortable-item-move-up`}>
        {button}
      </div>
    }
    return button
  }

  renderSelectedItemMoveDown (listItemId, withActionSidebar=true) {
    if (this.props.childExposedApi.selectedItemIsLast(listItemId)) {
      return null
    }
    const button = <button
      type={"button"}
      className="blocklist__action-button"
      aria-label="Move down"
      onClick={() => {this.onClickMoveDown(listItemId)}}>
      <span className="cricon cricon--chevron-down" aria-hidden="true" />
    </button>
    if (withActionSidebar) {
      return <div className="blocklist__action-sidebar" key={`${listItemId} sortable-item`}>
        {button}
      </div>
    }
    return button
  }

  renderSortableItems (listItemId) {
    if (this.props.inlineMoveIcons) {
      return [
        this.renderSelectedItemMoveUp(listItemId),
        this.renderSelectedItemMoveDown(listItemId)
      ]
    }
    return <div className="blocklist__action-sidebar" key={`${listItemId} sortable-item`}>
      {this.renderSelectedItemMoveUp(listItemId, false)}
      {this.renderSelectedItemMoveDown(listItemId, false)}
    </div>
  }

  renderSelectedItemContent (listItemId, listItemData) {
    let selectedItemContentList = super.renderSelectedItemContent(listItemId, listItemData)
    selectedItemContentList.push(
      this.renderSortableItems(listItemId)
    )
    return selectedItemContentList
  }
}
