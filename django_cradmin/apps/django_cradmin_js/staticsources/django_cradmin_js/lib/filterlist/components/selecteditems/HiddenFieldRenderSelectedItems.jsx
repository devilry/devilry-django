import React from 'react'
import PropTypes from 'prop-types'
import AbstractSelectedItems from './AbstractSelectedItems'
import 'ievv_jsbase/lib/utils/i18nFallbacks'

/**
 * Render selected items as hidden fields.
 *
 * See {@link HiddenFieldRenderSelectedItems.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "HiddenFieldRenderSelectedItems",
 *    "props": {
 *       "name": "my_selected_items"
 *    }
 * }
 *
 * @example <caption>Spec - debug mode</caption>
 * {
 *    "component": "HiddenFieldRenderSelectedItems",
 *    "props": {
 *       "name": "my_selected_items",
 *       "debug": true
 *    }
 * }
 */
export default class HiddenFieldRenderSelectedItems extends AbstractSelectedItems {
  static get propTypes () {
    return {
      ...super.propTypes,
      name: PropTypes.string.isRequired,
      debug: PropTypes.bool.isRequired
    }
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractSelectedItems.defaultProps}.
   *
   * @return {Object}
   * @property {string} name The name of the hidden field.
   *    This is required.
   *    **Must be provided in spec**.
   * @property {bool} debug If this is `true`, we render input elements of
   *    type "text" instead of "hidden". Nice for debugging.
   *    Defaults to `false`.
   *    **Can be used in spec**.
   */
  static get defaultProps () {
    return {
      ...super.defaultProps,
      name: null,
      debug: false
    }
  }

  get hiddenFieldType () {
    if (this.props.debug) {
      return 'text'
    }
    return 'hidden'
  }

  renderHiddenField (listItemId) {
    return <input
      key={listItemId}
      name={this.props.name}
      type={this.hiddenFieldType}
      defaultValue={listItemId} />
  }

  renderHiddenFields () {
    const renderedHiddenFields = []
    for (let listItemId of this.props.selectedListItemsMap.keys()) {
      renderedHiddenFields.push(this.renderHiddenField(listItemId))
    }
    return renderedHiddenFields
  }

  render () {
    if (this.props.selectedListItemsMap.size === 0) {
      return null
    }
    return <span>
      {this.renderHiddenFields()}
    </span>
  }
}
