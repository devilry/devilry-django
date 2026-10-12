import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from './AbstractFilter'
import * as gettext from 'ievv_jsbase/lib/gettext'

/**
 * Empty or boolean filter - users can select between "empty" or "true" or "false".
 *
 * See {@link EmptyBooleanFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "EmptyBooleanFilter",
 *    "props": {
 *      "name": "include_disabled_users",
 *      "label": "Include disabled users?"
 *    }
 * }
 *
 * @example <caption>Spec - with initial value</caption>
 * {
 *    "component": "EmptyBooleanFilter",
 *    "initialValue": true,
 *    "props": {
 *      "name": "include_disabled_users",
 *      "ariaLabel": "Include disabled users?"
 *    }
 * }
 *
 * @example <caption>Spec - with custom labels</caption>
 * {
 *    "component": "EmptyBooleanFilter",
 *    "initialValue": true,
 *    "props": {
 *      "name": "include_disabled_users",
 *      "ariaLabel": "Include disabled users?",
 *      "emptyLabel": "Any",
 *      "trueLabel": "Please do",
 *      "falseLabel": "Please do not"
 *    }
 * }
 */
export default class EmptyBooleanFilter extends AbstractFilter {
  static get propTypes () {
    const propTypes = super.propTypes
    propTypes.ariaLabel = PropTypes.string.isRequired
    propTypes.emptyLabel = PropTypes.string.isRequired
    propTypes.trueLabel = PropTypes.string.isRequired
    propTypes.falseLabel = PropTypes.string.isRequired
    propTypes.value = PropTypes.oneOfType([PropTypes.bool, PropTypes.string])
    propTypes.disabled = PropTypes.bool
    return propTypes
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractFilter.defaultProps}.
   *
   * @return {Object}
   * @property {string} ariaLabel The aria label of the select element.
   *    **Can be used in spec**.
   * @property {bool} value Must be true, false or null.
   */
  static get defaultProps () {
    const defaultProps = super.defaultProps
    defaultProps.value = null
    defaultProps.ariaLabel = null
    defaultProps.className = 'select select--outlined'
    defaultProps.emptyLabel = '---'
    defaultProps.trueLabel = gettext.gettext('Yes')
    defaultProps.falseLabel = gettext.gettext('No')
    defaultProps.disabled = false
    return defaultProps
  }

  static filterHttpRequest (httpRequest, name, value) {
    if (value === null) {
      return
    }
    super.filterHttpRequest(httpRequest, name, value)
  }

  static setInQueryString (queryString, name, value, allowNullInQuerystring = false) {
    if (!allowNullInQuerystring && value === null) {
      queryString.remove(name)
    } else {
      queryString.setSmart(name, value)
    }
  }

  static getValueFromQueryString (queryString, name) {
    const value = queryString.get(name, null)
    if (value === 'true') {
      return true
    } else if(value==='false'){
      return false
    }
    return null
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChange = this.onChange.bind(this)
  }

  optionValueToPropValue (optionValue) {
    switch (optionValue) {
      case 'empty':
        return null
      case 'true':
        return true
      default:
        return false
    }
  }

  propValueToOptionValue (value) {
    if (value === null) {
      return 'null'
    } else if (value) {
      return true
    }
    return false
  }

  onChange (e) {
    if (this.props.disabled) {
      return
    }
    this.setFilterValue(this.optionValueToPropValue(e.target.value))
  }

  get ariaLabel () {
    return this.props.ariaLabel
  }

  renderSelect () {
    return <select
      disabled={this.props.disabled}
      aria-label={this.ariaLabel}
      onChange={this.onChange}
      onFocus={this.onFocus}
      onBlur={this.onBlur}
      value={this.propValueToOptionValue(this.props.value)}
      key={'select'}
    >
      <option value={'empty'}>{this.props.emptyLabel}</option>
      <option value={'true'}>{this.props.trueLabel}</option>
      <option value={'false'}>{this.props.falseLabel}</option>
    </select>
  }

  renderLabelContent () {
    return [this.renderSelect()]
  }

  render () {
    return <label className={this.props.className}>
      {this.renderLabelContent()}
    </label>
  }
}
