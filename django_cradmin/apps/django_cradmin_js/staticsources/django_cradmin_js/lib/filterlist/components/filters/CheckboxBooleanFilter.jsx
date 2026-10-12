import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from './AbstractFilter'

/**
 * Checkbox filter that toggles a boolean.
 *
 * See {@link CheckboxBooleanFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "CheckboxBooleanFilter",
 *    "props": {
 *      "name": "include_disabled_users",
 *      "label": "Include disabled users?"
 *    }
 * }
 *
 * @example <caption>Spec - with initial value</caption>
 * {
 *    "component": "CheckboxBooleanFilter",
 *    "initialValue": true,
 *    "props": {
 *      "name": "include_disabled_users",
 *      "label": "Include disabled users?"
 *    }
 * }
 */
export default class CheckboxBooleanFilter extends AbstractFilter {
  static get propTypes () {
    const propTypes = super.propTypes
    propTypes.label = PropTypes.string.isRequired
    propTypes.value = PropTypes.bool.isRequired
    return propTypes
  }

  static getValueFromQueryString (queryString, name) {
    const value = queryString.getSmart(name)
    if (value === 'true') {
      return true
    } else if (value === 'false') {
      return false
    }
    return null
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractFilter.defaultProps}.
   *
   * @return {Object}
   * @property {string} label The label of the checkbox.
   *    **Can be used in spec**.
   */
  static get defaultProps () {
    const defaultProps = super.defaultProps
    defaultProps.value = false
    return defaultProps
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChange = this.onChange.bind(this)
  }

  onChange () {
    this.setFilterValue(!this.props.value)
  }

  renderLabel () {
    return this.props.label
  }

  get indicatorClassName () {
    return 'checkbox__control-indicator'
  }

  get labelClassName () {
    return 'checkbox checkbox--block'
  }

  renderInput () {
    return <input
      type='checkbox'
      checked={this.props.value}
      onChange={this.onChange}
      onFocus={this.onFocus}
      onBlur={this.onBlur} />
  }

  render () {
    return <label className={this.labelClassName}>
      {this.renderInput()}
      <span className={this.indicatorClassName} />
      {this.renderLabel()}
    </label>
  }
}
