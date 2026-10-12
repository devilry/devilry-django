import React from 'react'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'
import AbstractFilter from './AbstractFilter'
import BemUtilities from '../../../utilities/BemUtilities'

/**
 * Single choice filter.
 *
 * See {@link IntegerRangeFilter.defaultProps} for documentation for
 * props and their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 * {
 *    "component": IntegerRangeFilter,
 *    "props": {
 *       "name": "range",
 *       "label": "Range"
 * }
 *
 * @example <caption>Spec - with custom labels etc</caption>
 * {
 *    "component": IntegerRangeFilter,
 *    "props": {
 *       "fromPlaceholderText": "from",
 *       "toPlaceholderText": "to",
 *       "fromAriaLabel": "from",
 *       "toAriaLabel": "from",
 *       "name": "range",
 *       "label": "Range"
 * }
 */

/**
 * Integer range filter.
 *
 * See {@link IntegerRangeFilter.defaultProps} for documentation for props and
 * their defaults.
 *
 * @example <caption>Spec - minimal</caption>
 */
export default class IntegerRangeFilter extends AbstractFilter {
  static get propTypes () {
    return {
      ...super.propTypes,
      label: PropTypes.string.isRequired,
      value: PropTypes.object,
      bemBlock: PropTypes.string.isRequired,
      bemVariants: PropTypes.arrayOf(PropTypes.string)
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
      bemBlock: 'input',
      bemVariants: ['outlined']
    }
  }

  static filterHttpRequest (httpRequest, name, value) {
    if (value === null) {
      return null
    }
    if (value.fromValue === '' && value.toValue === '') {
      return
    }
    httpRequest.urlParser.queryString.set(`${name}_from`, value.fromValue)
    httpRequest.urlParser.queryString.set(`${name}_to`, value.toValue)
  }

  static setInQueryString (queryString, name, value, allowNullInQuerystring = false) {
    if (value === null) {
      queryString.remove(name)
    } else {
      queryString.setSmart(name, [value.fromValue, value.toValue].toString())
    }
  }

  static getValueFromQueryString (queryString, name) {
    let value = queryString.getSmart(name, null)
    if (value) {
      let resultValue = {}
      value = value.split(',')
      resultValue.fromValue = value[0]
      resultValue.toValue = value[1]
      return resultValue
    }

  }

  getInitialState () {
    return {
      fromValue: '',
      toValue: ''
    }
  }

  componentDidMount() {
    super.componentDidMount();
    if (this.props.value) {
      this.setState(this.props.value)
    }
  }

  setupBoundMethods () {
    super.setupBoundMethods()
    this.onChangeFrom = this.onChangeFrom.bind(this)
    this.onChangeTo = this.onChangeTo.bind(this)
  }

  parseValue (value) {
    // We need to return empty string since the input value is bound to the react state values.
    // Input value can not be null.
    if (value === null || value === '') {
      return ''
    }
    else {
      let parsedValue = Number.parseInt(value, 10)
      if (!Number.isInteger(parsedValue)) {
        return ''
      }
      return parsedValue
    }
  }

  onChangeFrom (e) {
    if (this.props.disabled) {
      return
    }
    this.setState({
      fromValue: this.parseValue(e.target.value)
    }, () => {
      this.setFilterValue(this.state)
    })
  }

  onChangeTo (e) {
    if (this.props.disabled) {
      return
    }
    this.setState({
      toValue: this.parseValue(e.target.value)
    }, () => {
      this.setFilterValue(this.state)
    })
  }

  get label () {
    return this.props.label
  }

  get className () {
    return BemUtilities.buildBemBlock(this.props.bemBlock, this.props.bemVariants)
  }

  get inputClassName () {
    return 'input input--inline input--width-xxsmall input--size-xsmall input--outlined'
  }

  get labelDomId () {
    return `${this.props.domIdPrefix}_input`
  }

  get fromInputDomId () {
    return `${this.props.domIdPrefix}_from_input`
  }

  get fromAriaLabel () {
    if (this.props.fromAriaLabel) {
      return this.props.fromAriaLabel
    }
    return `${this.props.label} (${gettext.pgettext('integer range filter', 'from')})`
  }

  get toAriaLabel () {
    if (this.props.toAriaLabel) {
      return this.props.toAriaLabel
    }
    return `${this.props.label} (${gettext.pgettext('integer range filter', 'to')})`
  }

  get fromPlaceholderText () {
    if (this.props.fromPlaceholderText) {
      return this.props.fromPlaceholderText
    }
    return gettext.pgettext('integer range filter placeholder from', 'from')
  }

  get toPlaceholderText () {
    if (this.props.toPlaceholderText) {
      return this.props.toPlaceholderText
    }
    return gettext.pgettext('integer range filter placeholder to', 'to')
  }

  render () {
    return <div className='fieldwrapper'>
      <label id={this.labelDomId} htmlFor={this.fromInputDomId} className={'label'} aria-hidden={true}>
          {this.label}
      </label>
      <input
        id={this.fromInputDomId}
        aria-label={this.fromAriaLabel}
        type="number"
        placeholder={this.fromPlaceholderText}
        className={this.inputClassName}
        value={this.state.fromValue}
        onChange={this.onChangeFrom}
        key={'from'}/>
      {' '}
      <input
        aria-label={this.toAriaLabel}
        type="number"
        placeholder={this.toPlaceholderText}
        className={this.inputClassName}
        value={this.state.toValue}
        onChange={this.onChangeTo}
        key={'to'}/>
    </div>
  }
}
