import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'
import * as gettext from 'ievv_jsbase/lib/gettext'
import AbstractHtml5DatetimeInput from './AbstractHtml5DatetimeInput'

export default class Html5DateInput extends AbstractHtml5DatetimeInput {
  static get defaultProps () {
    return {
      ...super.defaultProps,
      clearButtonTitle: gettext.pgettext('cradmin html5 date', 'Clear date'),
      onBlur: () => {}
    }
  }

  static get propTypes () {
    return {
      ...super.propTypes,
      onBlur: PropTypes.func
    }
  }

  valueStringToMoment (stringValue) {
    if (stringValue) {
      const momentValue = moment(stringValue)
      if (momentValue.isValid()) {
        return momentValue
      }
    }
    return null
  }

  get momentValue () {
    return this.valueStringToMoment(this.props.value)
  }

  makeValidInputFieldValue (valueString) {
    if (this.browserFullySupportsDateInput() || !valueString) {
      return valueString
    }

    const momentValue = moment(valueString)
    if (!momentValue.isValid()) {
      return valueString
    }
    return momentValue.format(this.inputFormat)
  }

  parseInputValue (stringValue) {
    let momentValue = null
    let isValid = true
    let isoStringValue = ''
    if (stringValue) {
      momentValue = moment(stringValue, this.inputFormat)
      if (momentValue.isValid()) {
        isoStringValue = momentValue.format('YYYY-MM-DD')
      } else {
        momentValue = null
        isValid = false
      }
    }
    return {
      isValid: isValid,
      momentValue: momentValue,
      isoStringValue: isoStringValue
    }
  }

  handleChange (stringValue) {
    stringValue = stringValue || ''
    this.setState({
      value: stringValue
    }, () => {
      const parseResult = this.parseInputValue(stringValue)
      this.props.onChange(parseResult.isoStringValue, parseResult.momentValue)
    })
  }

  onBlur (e) {
    let stringValue = e.target.value || ''
    const parseResult = this.parseInputValue(stringValue)
    if (parseResult.isoStringValue !== '') {
      stringValue = parseResult.momentValue.format(this.inputFormat)
    }
    this.setState({
      isBlurred: true,
      value: stringValue
    })
    this.props.onBlur(e)
  }

  getInputType () {
    return 'date'
  }

  get inputFormat () {
    if (this.browserFullySupportsDateInput()) {
      return 'YYYY-MM-DD'
    }
    return moment.localeData().longDateFormat('L')
  }

  get humanReadableInputFormat () {
    return gettext.pgettext('date format', this.inputFormat)
  }

  renderInput () {
    return <input {...this.inputProps} key={'date input'} />
  }

  renderInvalidInputText () {
    let prefix = ''
    if (this.state.isBlurred) {
      prefix = `${gettext.gettext('Invalid date format')}. `
    }
    const commonText = gettext.interpolate(
      gettext.gettext('Please type a date using this format: %(format)s'),
      {format: this.humanReadableInputFormat}, true
    )
    return `${prefix}${commonText}`
  }
}
