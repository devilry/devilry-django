import PropTypes from 'prop-types'
import AbstractLayoutComponentChild from '../AbstractLayoutComponentChild'

/**
 * Abstract base class for rendering components managing componentgroups.
 *
 * See {@link AbstractComponentGroup.defaultProps} for documentation for
 * props and their defaults.
 */
export default class AbstractComponentGroup extends AbstractLayoutComponentChild {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      enabledComponentGroups: PropTypes.instanceOf(Set).isRequired
    })
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractLayoutComponentChild.defaultProps}.
   *
   * @return {Object}
   * @property {Set} enabledComponentGroups Set of enabled componentgroups.
   *    _Provided automatically by the parent component_.
   */
  static get defaultProps () {
    return Object.assign(super.defaultProps, {
      enabledComponentGroups: null
    })
  }
}
