import React from 'react'
import PropTypes from 'prop-types'
import AbstractFilter from './AbstractFilter'
import BemUtilities from '../../../utilities/BemUtilities'

/**
 * DropDown filter where you can select different values.
 *
 * See {@link DropDownSelectFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": "DropDownSelectFilter",
 *    "props": {
 *      "options": [
 *        {
 *          "label": "Show all",
 *          "value": "all"
 *        }, {
 *          "label": "Evil only",
 *          "value": "evil"
 *        }, {
 *          "label": "Gods only",
 *          "value": "gods"
 *        }
 *      ],
 *      "value": "all"
 *    }
 * }
 */
export default class DropDownSelectFilter extends AbstractFilter {
  static get propTypes () {
    return Object.assign(super.propTypes, {
      options: PropTypes.arrayOf(PropTypes.object).isRequired,
      value: PropTypes.any,
      wrapperClassName: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string).isRequired
    })
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
    return Object.assign(super.defaultProps, {
      options: [],
      value: '',
      label: '',
      wrapperClassName: 'label',
      bemVariants: ['outlined', 'block']
    })
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChange = this.onChange.bind(this)
  }

  onChange (event) {
    this.setFilterValue(event.target.value)
  }

  get bemBlock () {
    return 'select'
  }

  get className () {
    return BemUtilities.addVariants(this.bemBlock, this.props.bemVariants)
  }

  get value () {
    return this.props.value === null ? '' : this.props.value
  }

  renderOptions () {
    const options = []
    for (const option of this.props.options) {
      options.push(
        <option value={option.value} key={option.value}>{option.label}</option>
      )
    }
    return options
  }

  render () {
    return <p className={this.props.wrapperClassName}>
      {this.props.label}
      <label className={this.className}>
        <select
          value={this.value}
          onChange={this.onChange}
          onFocus={this.onFocus}
          onBlur={this.onBlur}>
          {this.renderOptions()}
        </select>
      </label>
    </p>
  }
}
