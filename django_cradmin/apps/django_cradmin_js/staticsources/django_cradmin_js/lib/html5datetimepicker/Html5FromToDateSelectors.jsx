import React from 'react'
import PropTypes from 'prop-types'
import Html5DateInput from './Html5DateInput'
import * as gettext from 'ievv_jsbase/lib/gettext'
import moment from 'moment'

/**
* If you need to change the width on the date time fields, do as follows in the code
* which uses this date selector. Do not set lineItemWidth in this class!!:
*
*@example
*   component: Html5FromToDateSelectors
*    ...
*    dateSelectorProps: {
*      ...
*      commonDateOptions: {'lineItemWidth': 'medium'}
*    }
*
* The function `getLineItemWidth` gets the css class. If new css classes are added,
* update the switch in this function.
*
*/
export default class Html5FromToDateSelectors extends React.Component {
  static get propTypes () {
    return {
      fromDateValue: PropTypes.string.isRequired,
      toDateValue: PropTypes.string.isRequired,
      commonDateOptions: PropTypes.shape({}).isRequired,
      onChange: PropTypes.func.isRequired,
      isExpandedInitially: PropTypes.bool.isRequired,
      displayExpandToggle: PropTypes.bool.isRequired,
      label: PropTypes.string.isRequired,
      expandedLabel: PropTypes.string,
      expandToggleLabel: PropTypes.string.isRequired,
      toDateExpandedLabel: PropTypes.string.isRequired,
      fromDateExpandedLabel: PropTypes.string.isRequired
    }
  }

  static get defaultProps () {
    return {
      fromDateValue: '',
      toDateValue: '',
      label: null,
      expandedLabel: null,
      commonDateOptions: {},
      isExpandedInitially: false,
      displayExpandToggle: true,
      expandToggleLabel: gettext.pgettext('cradmin html5 from to date selector', 'Display to-date?'),
      toDateExpandedLabel: gettext.pgettext('cradmin html5 from to date selector', 'To date'),
      fromDateExpandedLabel: gettext.pgettext('cradmin html5 from to date selector', 'From date')
    }
  }

  constructor (props) {
    super(props)
    this.state = this.getInitialState()
    this.setupBoundFunctions()
  }

  /* initialization functions */

  getInitiallyExpanded () {
    if (this.props.isExpandedInitially) {
      return true
    } else if (this.props.fromDateValue !== this.props.toDateValue) {
      return true
    }
    return false
  }

  getInitialState () {
    return {
      isExpanded: this.getInitiallyExpanded(),
      invalidRangeAttempted: false
    }
  }

  setupBoundFunctions () {
    this.handleDateChange = this.handleDateChange.bind(this)
    this.handleShowToDateChange = this.handleShowToDateChange.bind(this)
    this.reset = this.reset.bind(this)
  }

  handleDateChange (valueKey, value) {
    const fromDate = valueKey === 'fromDate' ? value : this.props.fromDateValue
    const toDate = valueKey === 'toDate' ? value : this.props.toDateValue

    if (fromDate && toDate && this.state.isExpanded) {
      const momentFromDate = moment(fromDate)
      const momentToDate = moment(toDate)
      if (momentFromDate > momentToDate) {
        this.setState({
          invalidRangeAttempted: true
        })
        return
      }
    }

    if (this.state.invalidRangeAttempted) {
      this.setState({
        invalidRangeAttempted: false
      })
    }

    if (this.state.isExpanded) {
      this.props.onChange(fromDate, toDate)
    } else {
      this.props.onChange(fromDate, fromDate)
    }
  }

  handleShowToDateChange (event) {
    this.setState({
      isExpanded: event.target.checked
    }, () => {
      const fromDate = this.props.fromDateValue || ''
      this.props.onChange(fromDate, fromDate, true)
    })
  }

  reset () {
    this.props.onChange('', '', true)
  }

  get commonDateOptions () {
    return {
      ...this.props.commonDateOptions
    }
  }

  get fromDateMin () {
    return null
  }

  get fromDateMax () {
    if (!this.state.isExpanded) {
      return null
    }
    return this.props.toDateValue
  }

  get fromDateOptions () {
    return {
      ...this.commonDateOptions,
      value: this.props.fromDateValue,
      min: this.fromDateMin,
      max: this.fromDateMax,
      onChange: (value) => { this.handleDateChange('fromDate', value) },
      ariaLabel: this.ariaFromLabel
    }
  }

  get toDateMin () {
    if (!this.state.isExpanded) {
      return null
    }
    return this.props.fromDateValue
  }

  get toDateMax () {
    return null
  }

  get toDateOptions () {
    return {
      ...this.commonDateOptions,
      value: this.props.toDateValue,
      min: this.toDateMin,
      max: this.toDateMax,
      onChange: (value) => { this.handleDateChange('toDate', value) },
      ariaLabel: this.ariaToLabel
    }
  }

  get collapsedLabel () {
    return this.props.label
  }

  get expandedLabel () {
    if (this.props.expandedLabel) {
      return this.props.expandedLabel
    }
    return this.collapsedLabel
  }

  get label () {
    if (this.state.isExpanded) {
      return this.expandedLabel
    }
    return this.collapsedLabel
  }

  get toDateExpandedLabel () {
    return this.props.toDateExpandedLabel
  }

  get fromDateExpandedLabel () {
    return this.props.fromDateExpandedLabel
  }

  get expandToggleLabel () {
    return this.props.expandToggleLabel
  }

  get invalidRangeErrorMsg () {
    return gettext.pgettext('cradmin html5 from to date selector', 'To date cannot be before from date')
  }

  get ariaToLabel () {
    return `${this.expandedLabel}: ${this.toDateExpandedLabel}`
  }

  get ariaFromLabel () {
    if (this.state.isExpanded) {
      return `${this.expandedLabel}: ${this.fromDateExpandedLabel}`
    }
    return this.collapsedLabel
  }

  getLineItemWidth (fieldWrapperLineItemWidth) {
    switch (fieldWrapperLineItemWidth) {
      case 'xxsmall':
        return 'fieldwrapper-line__item--width-xxsmall'
      case 'xsmall':
        return 'fieldwrapper-line__item--width-xsmall'
      case 'medium':
        return 'fieldwrapper-line__item--width-medium'
      default:
        return 'fieldwrapper-line__item--width-small'
    }
  }

  /* Render functions */

  renderFromDateField () {
    return <Html5DateInput {...this.fromDateOptions} />
  }

  renderToDateField () {
    return <Html5DateInput {...this.toDateOptions} />
  }

  renderShowToFieldCheckbox () {
    if (!this.props.displayExpandToggle) {
      return null
    }
    return <label className='checkbox  checkbox--block'>
      <input type='checkbox' checked={this.state.isExpanded} onChange={this.handleShowToDateChange} />
      <span className='checkbox__control-indicator' />
      {this.expandToggleLabel}
    </label>
  }

  renderInvalidRangeError () {
    if (!this.state.invalidRangeAttempted) {
      return null
    }
    return <p className={'message message--error'}>{this.invalidRangeErrorMsg}</p>
  }

  renderIfExpandedLabel (labelText) {
    if (!this.state.isExpanded) {
      return null
    }
    return <label className={'label label--small label--muted'} aria-hidden>
      {labelText}
    </label>
  }

  renderLabel () {
    return <label className={'label'}>
      {this.label}
    </label>
  }

  renderToDateLayout () {
    if (!this.state.isExpanded) {
      return null
    }
    const lineItemWidth = this.getLineItemWidth(this.commonDateOptions.lineItemWidth)
    return <div className={'fieldwrapper-line__item ' + lineItemWidth}>
      <div className={'fieldwrapper fieldwrapper--compact'}>
        {this.renderIfExpandedLabel(this.toDateExpandedLabel)}
        {this.renderToDateField()}
      </div>
    </div>
  }

  renderDateFields () {
    const lineItemWidth = this.getLineItemWidth(this.commonDateOptions.lineItemWidth)
    return <div className={'fieldwrapper-line'}>
      <div className={'fieldwrapper-line__item ' + lineItemWidth}>
        <div className={'fieldwrapper fieldwrapper--compact'}>
          {this.renderIfExpandedLabel(this.fromDateExpandedLabel)}
          {this.renderFromDateField()}
        </div>
      </div>
      {this.renderToDateLayout()}
    </div>
  }

  render () {
    return <div className='fieldwrapper'>
      {this.renderLabel()}
      {this.renderDateFields()}
      {this.renderShowToFieldCheckbox()}
      {this.renderInvalidRangeError()}
    </div>
  }
}
