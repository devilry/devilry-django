import React from 'react'
import PropTypes from 'prop-types'
import AbstractLayoutComponentChild from '../AbstractLayoutComponentChild'

/**
 * Abstract base class for paginators.
 *
 * See {@link AbstractPaginator.defaultProps} for documentation for
 * props and their defaults.
 */
export default class AbstractPaginator extends AbstractLayoutComponentChild {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      listItemsDataArray: PropTypes.array.isRequired
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractLayoutComponentChild.defaultProps}.
   *
   * @return {Object}
   * @property {[]} listItemsDataArray The list of loaded items
   *    in the list. You normally do not need this in the paginator,
   *    but it is provided to force re-rendering when the items in
   *    the list changes.
   *    This is required, and defaults to `null`.
   *    _Provided automatically by the parent component_.
   */
  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      listItemsDataArray: null
    })
  }
}
