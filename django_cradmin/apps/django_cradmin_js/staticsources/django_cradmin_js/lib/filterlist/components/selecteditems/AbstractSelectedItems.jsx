import PropTypes from 'prop-types'
import AbstractLayoutComponentChild from '../AbstractLayoutComponentChild'

/**
 * Abstract base class for rendering selected items.
 *
 * See {@link AbstractSelectedItems.defaultProps} for documentation for
 * props and their defaults.
 */
export default class AbstractSelectedItems extends AbstractLayoutComponentChild {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      selectedListItemsMap: PropTypes.instanceOf(Map).isRequired
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractLayoutComponentChild.defaultProps}.
   *
   * @return {Object}
   * @property {Map} selectedListItemsMap Map of selected items
   *    (maps ID to item data).
   *    _Provided automatically by the parent component_.
   */
  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      selectedListItemsMap: null
    })
  }
}
