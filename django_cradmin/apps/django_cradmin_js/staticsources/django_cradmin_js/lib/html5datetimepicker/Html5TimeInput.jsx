import React from 'react'
import * as gettext from 'ievv_jsbase/lib/gettext'
import AbstractHtml5DatetimeInput from './AbstractHtml5DatetimeInput'

export default class Html5TimeInput extends AbstractHtml5DatetimeInput {
  static get defaultProps () {
    return {
      ...super.defaultProps,
      clearButtonTitle: gettext.pgettext('cradmin html5 date', 'Clear time')
    }
  }

  getInputType () {
    return 'time'
  }

  get inputFormat () {
    return 'HH:MM'
  }

  makeValidInputFieldValue (stringValue) {
    return stringValue
  }

  get humanReadableInputFormat () {
    return gettext.pgettext('time format', this.inputFormat)
  }

  static isValidTime (value) {
    return /^([0-1]?[0-9]|2[0-3]):([0-5][0-9])(:[0-5][0-9])?$/.test(value)
  }

  parseInputValue (stringValue) {
    let isValid = Html5TimeInput.isValidTime(stringValue)
    if (!isValid) {
      stringValue = ''
    }
    return {
      isValid: isValid,
      timeStringValue: stringValue
    }
  }

  onBlur (e) {
    let stringValue = e.target.value || ''
    const parseResult = this.parseInputValue(stringValue)
    this.setState({
      isBlurred: true,
      value: parseResult.timeStringValue
    })
  }

  handleChange (stringValue) {
    stringValue = stringValue || ''
    this.setState({
      value: stringValue
    }, () => {
      const parseResult = this.parseInputValue(stringValue)
      this.props.onChange(parseResult.timeStringValue)
    })
  }

  renderInvalidInputText () {
    let prefix = ''
    if (this.state.isBlurred) {
      prefix = `${gettext.gettext('Invalid time format')}. `
    }
    const commonText = gettext.interpolate(
      gettext.gettext('Please type a time using this format: %(format)s'),
      {format: this.humanReadableInputFormat}, true
    )
    return `${prefix}${commonText}`
  }

  renderInput () {
    return <input {...this.inputProps} key={'time input'} />
  }
}
