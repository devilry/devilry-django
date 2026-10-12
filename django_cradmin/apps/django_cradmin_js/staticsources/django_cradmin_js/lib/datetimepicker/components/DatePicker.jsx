import moment from 'moment'
import React from 'react'
import * as gettext from 'ievv_jsbase/lib/gettext'

import DateCalendar from './DateCalendar'

import PropTypes from 'prop-types'
import DatePickerToolbar from './DatePickerToolbar'
import BemUtilities from '../../utilities/BemUtilities'
import MomentRange from '../../utilities/MomentRange'

export default class DatePicker extends React.Component {
  static get defaultProps () {
    return {
      momentObject: null,
      initialFocusMomentObject: moment(),
      onChange: null,
      includeShortcuts: true,
      includeTodayButton: true,
      includeClearButton: true,
      momentRange: MomentRange.defaultForDatetimeSelect(),
      ariaDescribedByDomId: null
    }
  }

  static get propTypes () {
    return {
      momentObject: PropTypes.any,
      initialFocusMomentObject: PropTypes.any.isRequired,
      onChange: PropTypes.func.isRequired,
      includeShortcuts: PropTypes.bool,
      momentRange: PropTypes.instanceOf(MomentRange).isRequired,
      ariaDescribedByDomId: PropTypes.string.isRequired
    }
  }

  getMoment () {
    let momentObject = null
    if (this.props.momentObject === null) {
      momentObject = this.props.initialFocusMomentObject.clone()
    } else {
      momentObject = this.props.momentObject.clone()
    }
    return momentObject
  }

  get datePickerComponentClass () {
    return DateCalendar
  }

  get datePickerComponentProps () {
    return {
      key: 'datePicker',
      momentObject: this.props.momentObject,
      initialFocusMomentObject: this.props.initialFocusMomentObject,
      onDaySelect: this.onDaySelect.bind(this),
      momentRange: this.props.momentRange,
      ariaDescribedByDomId: this.props.ariaDescribedByDomId
    }
  }

  get toolbarComponentClass () {
    return DatePickerToolbar
  }

  get toolbarComponentProps () {
    return {
      key: 'toolbar',
      onPrevMonth: this.onPrevMonth.bind(this),
      onNextMonth: this.onNextMonth.bind(this),
      onMonthSelect: this.onMonthSelect.bind(this),
      onYearSelect: this.onYearSelect.bind(this),
      momentObject: this.getMoment(),
      momentRange: this.props.momentRange,
      ariaDescribedByDomId: this.props.ariaDescribedByDomId
    }
  }

  renderDatePicker () {
    const DatePickerComponent = this.datePickerComponentClass
    return <DatePickerComponent {...this.datePickerComponentProps} />
  }

  renderPicker () {
    return this.renderDatePicker()
  }

  renderToolbar () {
    const ToolbarComponent = this.toolbarComponentClass
    return <ToolbarComponent {...this.toolbarComponentProps} />
  }

  makeShortcutButtonClassName (bemVariants = []) {
    return BemUtilities.buildBemElement('buttonbar', 'button', [bemVariants, ...['compact']])
  }

  renderTodayButtonLabel () {
    return gettext.gettext('Today')
  }

  get shouldRenderTodayButton () {
    return this.props.includeTodayButton
  }

  renderTodayButton () {
    if (!this.shouldRenderTodayButton) {
      return null
    }
    return <button
      type={'button'}
      key={'todayButton'}
      className={this.makeShortcutButtonClassName()}
      onClick={this.onClickTodayButton.bind(this)}
    >
      {this.renderTodayButtonLabel()}
    </button>
  }

  renderClearButtonLabel () {
    return gettext.pgettext('clear date field', 'Clear')
  }

  get shouldRenderClearButton () {
    if (!this.props.includeClearButton) {
      return false
    }
    return this.props.momentObject !== null
  }

  renderClearButton () {
    if (!this.shouldRenderClearButton) {
      return null
    }
    return <button
      type={'button'}
      key={'clearButton'}
      className={this.makeShortcutButtonClassName()}
      onClick={this.onClickClearButton.bind(this)}
    >
      {this.renderClearButtonLabel()}
    </button>
  }

  _removeNulls (itemArray) {
    let result = []
    for (let item of itemArray) {
      if (item !== null) {
        result.push(item)
      }
    }
    return result
  }

  renderShortcutButtons () {
    return [
      this.renderTodayButton(),
      this.renderClearButton()
    ]
  }

  renderShortcutButtonBar () {
    const renderedShortcutButtons = this._removeNulls(this.renderShortcutButtons())
    if (renderedShortcutButtons.length === 0) {
      return null
    }
    return <div key={'shortcutButtonBar'} className={'text-center'}>
      <div className={'buttonbar buttonbar--inline'}>
        {renderedShortcutButtons}
      </div>
    </div>
  }

  render () {
    return [
      this.renderToolbar(),
      this.renderPicker(),
      this.props.includeShortcuts ? this.renderShortcutButtonBar() : null
    ]
  }

  onPrevMonth (e) {
    e.preventDefault()
    let momentObject = this.getMoment().clone()
    this.props.onChange(momentObject.subtract(1, 'month'))
  }

  onNextMonth (e) {
    e.preventDefault()
    let momentObject = this.getMoment().clone()
    this.props.onChange(momentObject.add(1, 'month'))
  }

  onClickTodayButton () {
    const today = moment()
    let momentObject = this.getMoment().clone()
    momentObject.year(today.year())
    momentObject.month(today.month())
    momentObject.date(today.date())
    this.props.onChange(momentObject)
  }

  onClickClearButton () {
    this.props.onChange(null, true, true)
  }

  onDaySelect (dayMomentObject) {
    this.props.onChange(this.props.momentRange.getClosestValid(dayMomentObject), true, false)
  }

  onMonthSelect (monthNumber) {
    let momentObject = this.getMoment().clone().month(monthNumber)
    momentObject = this.props.momentRange.getClosestValid(momentObject)
    this.props.onChange(momentObject)
  }

  onYearSelect (year) {
    let momentObject = this.getMoment().clone().year(year)
    momentObject = this.props.momentRange.getClosestValid(momentObject)
    this.props.onChange(momentObject)
  }
}
