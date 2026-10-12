import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from './AbstractFilter'
import BemUtilities from '../../../utilities/BemUtilities'

/**
 * Single choice filter.
 *
 * See {@link SingleChoiceFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "SingleChoiceFilter",
 *    "props": {
 *      "name": "size",
 *      "label": "Size?",
 *      "choices": [
 *        {"value": "l", "label": "Large"},
 *        {"value": "m", "label": "Medium"},
 *        {"value": "s", "label": "Small"},
 *      ]
 *    }
 * }
 *
 * @example <caption>Spec - with initial value</caption>
 * {
 *    "component": "SingleChoiceFilter",
 *    "initialValue": "l",
 *    "props": {
 *      "name": "size",
 *      "label": "Size?",
 *      "choices": [
 *        {"value": "l", "label": "Large"},
 *        {"value": "m", "label": "Medium"},
 *        {"value": "s", "label": "Small"},
 *      ]
 *    }
 * }
 */
export default class SingleChoiceFilter extends AbstractFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      label: PropTypes.string.isRequired,
      value: PropTypes.string,
      disabled: PropTypes.bool.isRequired,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string),
      choices: PropTypes.arrayOf(PropTypes.object).isRequired
    }
  }

  /**
   * Get default props. Extends the default props
   * from {@link AbstractFilter.defaultProps}.
   *
   * @return {Object}
   * @property {string} label The aria label of the select element.
   *    **Can be used in spec**.
   * @property {bool} disabled Is the filter disabled? Defaults to ``false``.
   * @property {[]} choices The choices for the filter as an array of objects,
   *    where each object must have ``value`` and ``label`` keys.
   * @property {string} value The value as a string.
   */
  static get defaultProps () {
    return {
      ...super.defaultProps,
      value: null,
      label: null,
      bemBlock: 'select',
      bemVariants: ['outlined'],
      disabled: false,
      options: null
    }
  }

  static filterHttpRequest (httpRequest, name, value) {
    if (value === null) {
      return
    }
    super.filterHttpRequest(httpRequest, name, value)
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChange = this.onChange.bind(this)
  }

  /**
   * Convert option value to option value.
   *
   * Just returns the provided value by default, but may be useful in subclasses.
   *
   * @param optionValue
   * @returns {*}
   */
  optionValueToPropValue (optionValue) {
    return optionValue
  }

  /**
   * Convert prop value to option value.
   *
   * Just returns the provided value by default, but may be useful in subclasses.
   *
   * @param propValue
   * @returns {*}
   */
  propValueToOptionValue (propValue) {
    return propValue
  }

  onChange (e) {
    if (this.props.disabled) {
      return
    }
    this.setFilterValue(this.optionValueToPropValue(e.target.value))
  }

  get label () {
    return this.props.label
  }

  get className () {
    return BemUtilities.buildBemBlock(this.props.bemBlock, this.props.bemVariants)
  }

  renderOption (choice) {
    return <option key={choice.value} value={choice.value}>{choice.label}</option>
  }

  renderOptions () {
    let renderedOptions = []
    for(let choice of this.props.choices) {
      renderedOptions.push(this.renderOption(choice))
    }
    return renderedOptions
  }

  renderSelect () {
    return <select
      disabled={this.props.disabled}
      aria-label={this.label}
      onChange={this.onChange}
      onFocus={this.onFocus}
      onBlur={this.onBlur}
      value={this.propValueToOptionValue(this.props.value)}
      key={'select'}
    >
      {this.renderOptions()}
    </select>
  }

  renderLabelContent () {
    return [this.renderSelect()]
  }

  render () {
    return <label className={this.className}>
      {this.renderLabelContent()}
    </label>
  }
}
